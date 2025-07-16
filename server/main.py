import os
import json
import asyncio
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Annotated
from typing_extensions import TypedDict

from langchain_community.chat_models import ChatLlamaCpp
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import DATA_DIR, logger
from app.utils import sse_headers
from app.rag import RAGAgent, IndexReloadHandler
from app.research import ResearchAgent

# --- State Type ---
from langgraph.graph.message import add_messages
class State(TypedDict):
    messages: Annotated[list, add_messages]

# --- LLM ---
def get_llm():
    return ChatLlamaCpp(
        model_path="model/jan-nano-128k-Q5_K_M.gguf", # path to your model
        verbose=False,
        temperature=0.1,
        n_ctx=12000
    )
LLM = get_llm()

# --- Agents ---
rag_agent = RAGAgent(DATA_DIR, "./store_rag", LLM)
research_agent = ResearchAgent(LLM, State)

# --- FastAPI Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    from watchdog.observers import Observer
    observer = Observer()
    handler = IndexReloadHandler(loop, rag_agent)
    observer.schedule(handler, path=DATA_DIR, recursive=False)
    observer.start()
    logger.info("[RAG Watcher] Started file monitoring.")
    yield
    observer.stop()
    observer.join()
    logger.info("[RAG Watcher] Stopped.")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RAG Endpoints ---
@app.post("/rag/upload/")
async def rag_upload_file(file: UploadFile = File(...)):
    path = os.path.join(DATA_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    await rag_agent.reload_index()
    return {"message": f"Uploaded and indexed {file.filename}"}

@app.get("/rag/files/")
def rag_list_files():
    return {"files": os.listdir(DATA_DIR)}

@app.delete("/rag/delete/{filename}")
async def rag_delete_file(filename: str):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
        await rag_agent.reload_index()
        return {"message": f"Deleted {filename} and re-indexed"}
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/rag/stream")
async def rag_stream_response(request: Request, user_input: str, thread_id: int = 1):
    if not user_input:
        raise HTTPException(status_code=400, detail="Missing user_input")
    graph = rag_agent.build_graph(State)
    async def event_generator():
        try:
            config = {"configurable": {"thread_id": str(thread_id)}}
            data = {"messages": [HumanMessage(content=user_input)]}
            yield f"event: user\ndata: {json.dumps({'content': user_input})}\n\n"
            yield f"event: start\ndata: {json.dumps({'content': 'Assistant:'})}\n\n"
            in_tool = False
            async for ev in graph.astream_events(data, config=config, version="v2"):
                if await request.is_disconnected():
                    break
                if ev["event"] == "on_chat_model_stream":
                    token = ev["data"]["chunk"].content
                    if "<tool_call>" in token:
                        in_tool = True
                    elif "</tool_call>" in token:
                        in_tool = False
                        continue
                    if not in_tool and token:
                        yield f"event: token\ndata: {json.dumps({'content': token})}\n\n"
                elif ev["event"] == "on_tool_start":
                    inp = ev["data"]["input"]
                    qry = inp.get("query") or inp.get("input", "")
                    yield f"event: search\ndata: {json.dumps({'content': f'🔎 Searching: {qry}'})}\n\n"
            yield f"event: done\ndata: {json.dumps({'content': '[DONE]'})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=sse_headers())

# --- Research Endpoint ---
@app.get("/research/stream")
async def research_stream_response(request: Request, user_input: str, thread_id: int = 1):
    if not user_input:
        raise HTTPException(status_code=400, detail="Missing user_input")
    graph = research_agent.graph
    async def event_generator():
        try:
            config = {"configurable": {"thread_id": str(thread_id)}}
            data = {"messages": [
                SystemMessage(content="You are a helpful assistant.Your name is Parkky. Dont use include_domains argument during search."),
                HumanMessage(content=user_input)
            ]}
            in_tool_call = False
            yield f"event: user\ndata: {json.dumps({'content': user_input})}\n\n"
            yield f"event: start\ndata: {json.dumps({'content': 'Assistant:'})}\n\n"
            async for ev in graph.astream_events(data, config=config, version="v2"):
                if await request.is_disconnected():
                    break
                if ev["event"] == "on_chat_model_stream":
                    token = ev["data"]["chunk"].content
                    if "<tool_call>" in token:
                        in_tool_call = True
                    elif "</tool_call>" in token:
                        in_tool_call = False
                        continue
                    if not in_tool_call and token:
                        yield f"event: token\ndata: {json.dumps({'content': token})}\n\n"
                elif ev["event"] == "on_tool_start":
                    inp = ev["data"]["input"]
                    qry = inp.get("query") or inp.get("input", "")
                    yield f"event: search\ndata: {json.dumps({'content': f'🔎 Searching: {qry}'})}\n\n"
                elif ev["event"] == "on_tool_end":
                    tool_output = ev["data"].get("output", {})
                    results = tool_output.get("results", [])
                    if results:
                        yield f"event: urls\ndata: {json.dumps({'content': '🌐 Top Search Results:'})}\n\n"
                        for i, result in enumerate(results, start=1):
                            url = result.get("url")
                            title = result.get("title", "")
                            if url:
                                yield f"event: urls\ndata: {json.dumps({'content': f'{i}. {title}\\n   {url}'})}\n\n"
            yield f"event: done\ndata: {json.dumps({'content': '[DONE]'})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=sse_headers())

# --- Health Endpoint ---
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# --- Entrypoint ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
