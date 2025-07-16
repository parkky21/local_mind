import os
import json
import uuid
import asyncio
from watchdog.events import FileSystemEventHandler
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from llama_index.core import (
    SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage, Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .config import DATA_DIR, RAG_STORE_DIR, logger
from .utils import parse_tool_call_from_content

splitter = SentenceSplitter(chunk_size=256, chunk_overlap=50)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

class BasicToolNode:
    def __init__(self, tools: list):
        self.tools_by_name = {tool.name: tool for tool in tools}
    def __call__(self, inputs: dict):
        messages = inputs.get("messages", [])
        last_message = messages[-1]
        content = getattr(last_message, "content", "") if hasattr(last_message, "content") else last_message.get("content", "")
        tool_data = parse_tool_call_from_content(content)
        name = tool_data["name"]
        args = tool_data["arguments"]
        if name not in self.tools_by_name:
            raise ValueError(f"Tool {name} not registered")
        result = self.tools_by_name[name].invoke(args)
        return {
            "messages": [
                ToolMessage(content=json.dumps(result), name=name, tool_call_id=str(uuid.uuid4()))
            ]
        }

class RAGAgent:
    def __init__(self, data_dir, store_dir, llm):
        self.data_dir = data_dir
        self.store_dir = store_dir
        self.index = None
        self.index_lock = asyncio.Lock()
        self.tools = []
        self.llm = llm
        self._load_or_rebuild_index()
    def _register_tools(self):
        @tool
        def query_info(query: str) -> dict:
            """Use this tool to search in the knowledge base."""
            retriever = self.index.as_retriever(similarity_top_k=4)
            nodes = retriever.retrieve(query)
            results = []
            for i, nw in enumerate(nodes):
                node = nw.node
                results.append({
                    "result_number": i + 1,
                    "file_name": node.metadata.get("file_name", "Unknown"),
                    "page_number": node.metadata.get("page_label", "Unknown"),
                    "content": node.text.strip(),
                    "score": nw.score
                })
            return {"query": query, "results": results, "total_results": len(results)}
        self.tools.clear()
        self.tools.append(query_info)
    def _rebuild_index(self):
        try:
            docs = SimpleDirectoryReader(self.data_dir).load_data()
            if not docs:
                logger.warning("No files to index in %s.", self.data_dir)
                self.index = None
                self.tools = []
                return
            self.index = VectorStoreIndex.from_documents(docs, transformations=[splitter])
            self.index.storage_context.persist(persist_dir=self.store_dir)
            logger.info("RAG index rebuilt and persisted.")
            self._register_tools()
        except ValueError as ve:
            logger.warning("No files found to index: %s", ve)
            self.index = None
            self.tools = []
            self._register_tools()
    def _load_or_rebuild_index(self):
        if os.path.exists(self.store_dir) and os.listdir(self.store_dir):
            sc = StorageContext.from_defaults(persist_dir=self.store_dir)
            self.index = load_index_from_storage(sc)
            logger.info("RAG index loaded from storage.")
            self._register_tools()
        else:
            self._rebuild_index()
    async def reload_index(self):
        async with self.index_lock:
            try:
                self._rebuild_index()
                logger.info("[RAG Watcher] Index successfully reloaded.")
            except Exception as e:
                logger.error(f"[RAG Watcher] Index reload failed: {e}")
    def get_tools(self):
        return self.tools
    def get_tool_node(self):
        return BasicToolNode(self.tools)
    def get_llm_with_tools(self):
        return self.llm.bind_tools(self.tools)
    def build_graph(self, State):
        tool_node = self.get_tool_node()
        llm_with_tools = self.get_llm_with_tools()
        def chatbot(state: State):
            return {"messages": [llm_with_tools.invoke(state["messages"])]}
        def route_tools(state: State):
            last = state["messages"][-1].content
            return "tools" if "<tool_call>" in last else END
        gb = StateGraph(State)
        gb.add_node("chatbot", chatbot)
        gb.add_node("tools", tool_node)
        gb.set_entry_point("chatbot")
        gb.add_conditional_edges("chatbot", route_tools, {"tools": "tools", END: END})
        gb.add_edge("tools", "chatbot")
        gb.add_edge(START, "chatbot")
        return gb.compile(checkpointer=MemorySaver())

class IndexReloadHandler(FileSystemEventHandler):
    def __init__(self, loop, agent):
        super().__init__()
        self.loop = loop
        self.agent = agent
    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.event_type in ("created", "modified", "deleted"):
            logger.info(f"[RAG Watcher] File change detected: {event.src_path}")
            asyncio.run_coroutine_threadsafe(self.agent.reload_index(), self.loop)
