# --- SECTION A: IMPORTS & CONFIG ---
import os
import uuid
import time
import json
import asyncio
import traceback
import base64
import logging # Added for ground truth
from google.cloud import firestore, storage
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any, Literal, Tuple
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI, HarmBlockThreshold, HarmCategory
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
from langchain_core.load import dumpd, load
from pydantic import BaseModel, Field
from app.tools import update_board, write_file
from langserve import add_routes

# --- IMPORT THE AGENCY HUB ---
from app.agency.architect import router as architect_router

# SETUP LOGGING
logger = logging.getLogger("uvicorn.error")

# --- SECTION B: CLOUD INITIALIZATION ---
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
storage_client = storage.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
BUCKET_NAME = "vibe-agent-user-projects"
REGION = "us-central1"

# --- SECTION C: CO-FOUNDER LOGIC ---
COFOUNDER_PROMPT = "You are 'The Co-Founder' – a strategic partner."
SCRIBE_PROMPT = "You are 'The Scribe' (Background Process)."

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
}

llm_chat = ChatVertexAI(model_name="gemini-2.5-pro", project=os.environ.get("GCP_PROJECT"), location=REGION, transport="rest", safety_settings=safety_settings)
llm_scribe = ChatVertexAI(model_name="gemini-2.5-flash", project=os.environ.get("GCP_PROJECT"), location=REGION, transport="rest", safety_settings=safety_settings)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def call_model(state: AgentState):
    return {"messages": [llm_chat.invoke(state["messages"])]}

workflow = StateGraph(AgentState)
workflow.add_node("cofounder", call_model)
workflow.set_entry_point("cofounder")
workflow.add_edge("cofounder", END)

# --- SECTION D: PERSISTENCE (FIRESTORE) ---
class TypedSerializer:
    def dumps_typed(self, obj: Any) -> Tuple[str, bytes]:
        return "json", json.dumps(dumpd(obj)).encode("utf-8")
    def loads_typed(self, data: Tuple[str, bytes]) -> Any:
        return load(json.loads(data[1].decode("utf-8")))

class CustomFirestoreSaver(BaseCheckpointSaver):
    def __init__(self, client: firestore.Client, collection: str = "checkpoints"):
        super().__init__(serde=TypedSerializer())
        self.client = client
        self.collection = collection
    async def aget_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        docs = list(self.client.collection(self.collection).where("thread_id", "==", thread_id).order_by("checkpoint_id", direction=firestore.Query.DESCENDING).limit(1).stream())
        if not docs: return None
        data = docs[0].to_dict()
        return CheckpointTuple(config, self.serde.loads_typed(("json", data["checkpoint"].encode("utf-8"))), self.serde.loads_typed(("json", data["metadata"].encode("utf-8"))), None)
    async def aput(self, config, checkpoint, metadata, new_versions):
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = f"{int(time.time()*1000)}"
        _, chk_bytes = self.serde.dumps_typed(checkpoint)
        _, meta_bytes = self.serde.dumps_typed(metadata)
        self.client.collection(self.collection).document(f"{thread_id}_{checkpoint_id}").set({"thread_id": thread_id, "checkpoint_id": checkpoint_id, "checkpoint": chk_bytes.decode("utf-8"), "metadata": meta_bytes.decode("utf-8"), "created_at": firestore.SERVER_TIMESTAMP})
        return {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}
    async def aput_writes(self, config, writes, task_id, task_path=""): pass
    def list(self, config, **kwargs): return []
    async def alist(self, config, **kwargs): return []
    def get_tuple(self, config): return None 
    def put(self, config, checkpoint, metadata, new_versions): return {}

checkpointer = CustomFirestoreSaver(db, "custom_checkpoints")
graph = workflow.compile(checkpointer=checkpointer)

# --- SECTION E: BACKGROUND SCRIBE ---
class ScribeOutput(BaseModel):
    vision: str; tasks: str; project_name: str

async def run_scribe_background(thread_id: str):
    try:
        state = await graph.aget_state({"configurable": {"thread_id": thread_id}})
        if not state.values: return
        history = ""
        for msg in state.values.get("messages", []):
            if isinstance(msg, (HumanMessage, AIMessage)): history += f"{msg.content}\n"
        scribe_chain = ChatPromptTemplate.from_messages([("system", SCRIBE_PROMPT), ("human", "{history}")]) | llm_scribe.with_structured_output(ScribeOutput)
        res = await scribe_chain.ainvoke({"history": history})
        db.collection("cofounder_boards").document(thread_id).set({"project_name": res.project_name, "vision": res.vision, "updated_at": firestore.SERVER_TIMESTAMP}, merge=True)
    except Exception: pass

# --- SECTION F: THE API (STABILIZED) ---
app = FastAPI(title="The Co-Founder")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(architect_router, prefix="/agent/design", tags=["Architect"])

@app.get("/")
async def root():
    return {"status": "AGENCY ONLINE", "version": "1.2.6"}

@app.get("/agent/projects")
async def list_projects():
    docs = db.collection("cofounder_boards").order_by("is_pinned", direction=firestore.Query.DESCENDING).order_by("updated_at", direction=firestore.Query.DESCENDING).limit(50).stream()
    return {"projects": [{"thread_id": d.id, "project_name": d.to_dict().get("project_name", "Untitled"), "updated_at": d.to_dict().get("updated_at").isoformat() if d.to_dict().get("updated_at") else None, "is_pinned": d.to_dict().get("is_pinned", False)} for d in docs]}

@app.post("/agent/projects/init")
async def init_project(req: dict):
    thread_id = req.get("thread_id")
    db.collection("cofounder_boards").document(thread_id).set({
        "project_name": req.get("project_name", "UNTITLED PROJECT"),
        "is_pinned": False,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "vibe_manifest": None
    })
    return {"status": "success"}

@app.get("/agent/projects/{thread_id}")
async def get_project(thread_id: str):
    doc = db.collection("cofounder_boards").document(thread_id).get()
    return doc.to_dict() if doc.exists else {"error": "not found"}

@app.post("/agent/projects/save")
async def save_project(req: dict):
    thread_id = req.get("thread_id")
    
    # 🛡️ SHIELD: Validate thread_id exists before updating document
    if not thread_id:
        logger.error("❌ SAVE FAILED: No thread_id provided in request body")
        raise HTTPException(status_code=400, detail="Missing thread_id")

    db.collection("cofounder_boards").document(thread_id).update({
        "vibe_manifest": req.get("manifest"),
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    return {"status": "success"}

@app.post("/agent/thread/{thread_id}/rename")
async def rename_thread(thread_id: str, req: dict):
    db.collection("cofounder_boards").document(thread_id).update({"project_name": req.get("name")})
    return {"status": "success"}

@app.post("/agent/thread/{thread_id}/pin")
async def toggle_pin(thread_id: str):
    doc_ref = db.collection("cofounder_boards").document(thread_id)
    doc_snap = doc_ref.get()
    if doc_snap.exists:
        curr = doc_snap.to_dict().get("is_pinned", False)
        doc_ref.update({"is_pinned": not curr})
    return {"status": "success"}

@app.delete("/agent/thread/{thread_id}")
async def delete_thread(thread_id: str):
    db.collection("cofounder_boards").document(thread_id).delete()
    return {"status": "success"}

@app.get("/health")
def health(): return {"status": "OK"}

add_routes(app, graph, path="/agent_debug")