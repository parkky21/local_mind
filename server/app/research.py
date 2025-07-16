from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .rag import BasicToolNode
from .config import logger

class ResearchAgent:
    def __init__(self, llm, State):
        self.llm = llm
        self.tavily = TavilySearch(max_results=4, topic="general")
        self.tools = [self.tavily]
        self.tool_node = BasicToolNode(self.tools)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.graph = self._build_graph(State)
    def _build_graph(self, State):
        def chatbot(state: State):
            return {"messages": [self.llm_with_tools.invoke(state["messages"])]}
        def route_tools(state: State):
            messages = state.get("messages", [])
            if not messages:
                return END
            last_message = messages[-1]
            content = getattr(last_message, "content", "") if hasattr(last_message, "content") else last_message.get("content", "")
            if "<tool_call>" in content and "</tool_call>" in content:
                logger.info("ResearchAgent: websearch initiated")
                return "tools"
            return END
        gb = StateGraph(State)
        gb.add_node("chatbot", chatbot)
        gb.add_node("tools", self.tool_node)
        gb.set_entry_point("chatbot")
        gb.add_conditional_edges("chatbot", route_tools, {"tools": "tools", END: END})
        gb.add_edge("tools", "chatbot")
        gb.add_edge(START, "chatbot")
        return gb.compile(checkpointer=MemorySaver())
