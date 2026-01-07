import os
import uuid
import time
import json
import asyncio
import traceback
import base64
from google.cloud import firestore, storage
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any, Literal, Tuple
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_vertexai import ChatVertexAI, HarmBlockThreshold, HarmCategory
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
from langchain_core.load import dumpd, load
from pydantic import BaseModel, Field
from app.tools import update_board, write_file
from langserve import add_routes

# --- IMPORT THE NEW ARCHITECT BRAIN ---
from app.agency.architect import router as architect_router

# --- 1. INITIALIZATION ---
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
storage_client = storage.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
BUCKET_NAME = "vibe-agent-user-projects"
REGION = "us-central1"

# --- 2. CONFIG & PROMPTS ---
COFOUNDER_PROMPT = """You are "The Co-Founder" – a strategic partner.
YOUR ROLE:
1. Listen to the user's ideas.
2. Be enthusiastic but critical (challenge weak points).
3. Ask clarifying questions to help them flesh out the vision.
4. DO NOT worry about saving or structuring data. Just have a great conversation.
"""

SCRIBE_PROMPT = """You are "The Scribe" (Background Process).
YOUR ROLE:
1. Read the conversation history provided.
2. Extract the "Project Vision" (High level goals, "Soul" of the idea).
3. Extract the "Roadmap/Tasks" (Specific actionable steps).
4. Extract a "Project Name" (Short, punchy title, 2-5 words).
5. Output structured data to update the Knowledge Base."""

# --- 3. MODEL SETUP ---
safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
}

llm_chat = ChatVertexAI(
    model_name="gemini-2.5-pro",
    project=os.environ.get("GCP_PROJECT", "vibe-agent-final"),
    location=REGION,
    temperature=0.7,
    transport="rest", 
    safety_settings=safety_settings,
)

llm_scribe = ChatVertexAI(
    model_name="gemini-2.5-flash",
    project=os.environ.get("GCP_PROJECT", "vibe-agent-final"),
    location=REGION,
    temperature=0.1,
    transport="rest",
    safety_settings=safety_settings,
)

# --- 4. THE CHAT GRAPH ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def call_model(state: AgentState):
    raw_messages = state["messages"]
    clean_messages = []
    
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        user_profile = ""
        blob_profile = bucket.blob("USER_PROFILE.md")
        if blob_profile.exists(): user_profile = blob_profile.download_as_text()
            
        project_index = ""
        blob_index = bucket.blob("PROJECT_INDEX.md")
        if blob_index.exists(): project_index = blob_index.download_as_text()
        
        dynamic_system_prompt = f"""{COFOUNDER_PROMPT}
### MEMORY CONTEXT
{user_profile}
{project_index}
Use this context to recognize the user and their projects."""
        clean_messages.append(SystemMessage(content=dynamic_system_prompt))
    except Exception:
        clean_messages.append(SystemMessage(content=COFOUNDER_PROMPT))
    
    for msg in raw_messages:
        if isinstance(msg, SystemMessage): continue
        if isinstance(msg, (HumanMessage, AIMessage)): clean_messages.append(msg)
        elif isinstance(msg, ToolMessage): clean_messages.append(HumanMessage(content=f"[System Log]: {msg.content}"))
        else: clean_messages.append(HumanMessage(content=str(msg.content)))
            
    response = llm_chat.invoke(clean_messages)
    return {"messages": [response]}

workflow = StateGraph(AgentState)
workflow.add_node("cofounder", call_model)
workflow.set_entry_point("cofounder")
workflow.add_edge("cofounder", END)

class TypedSerializer:
    def dumps_typed(self, obj: Any) -> Tuple[str, bytes]:
        data = dumpd(obj)
        json_bytes = json.dumps(data).encode("utf-8")
        return "json", json_bytes

    def loads_typed(self, data: Tuple[str, bytes]) -> Any:
        if data[0] != "json": raise ValueError(f"Unknown serialization type: {data[0]}")
        json_str = data[1].decode("utf-8")
        obj_dict = json.loads(json_str)
        return load(obj_dict)

class CustomFirestoreSaver(BaseCheckpointSaver):
    def __init__(self, client: firestore.Client, collection: str = "checkpoints"):
        super().__init__(serde=TypedSerializer())
        self.client = client
        self.collection = collection

    async def aget_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        query = (self.client.collection(self.collection)
            .where("thread_id", "==", thread_id)
            .order_by("checkpoint_id", direction=firestore.Query.DESCENDING).limit(1))
        docs = list(query.stream())
        if not docs: return None
        data = docs[0].to_dict()
        checkpoint = self.serde.loads_typed(("json", data["checkpoint"].encode("utf-8")))
        metadata = self.serde.loads_typed(("json", data["metadata"].encode("utf-8")))
        return CheckpointTuple({"configurable": {"thread_id": thread_id, "checkpoint_ns": "", "checkpoint_id": data["checkpoint_id"]}}, checkpoint, metadata, None)

    async def aput(self, config, checkpoint, metadata, new_versions):
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"].get("checkpoint_id") or f"{int(time.time()*1000)}_{str(uuid.uuid4())[:8]}"
        _, chk_bytes = self.serde.dumps_typed(checkpoint)
        _, meta_bytes = self.serde.dumps_typed(metadata)
        doc_data = {
            "thread_id": thread_id, 
            "checkpoint_id": checkpoint_id, 
            "checkpoint": chk_bytes.decode("utf-8"), 
            "metadata": meta_bytes.decode("utf-8"), 
            "created_at": firestore.SERVER_TIMESTAMP
        }
        await asyncio.to_thread(self.client.collection(self.collection).document(f"{thread_id}_{checkpoint_id}").set, doc_data)
        return {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}
    
    async def aput_writes(self, config, writes, task_id, task_path=""): pass
    def list(self, config, **kwargs): return []
    async def alist(self, config, **kwargs): return []
    def get_tuple(self, config): return None 
    def put(self, config, checkpoint, metadata, new_versions): return {}

checkpointer = CustomFirestoreSaver(db, "custom_checkpoints")
graph = workflow.compile(checkpointer=checkpointer)

# --- 6. BACKGROUND WORKERS (THE SCRIBE) ---
class ScribeOutput(BaseModel):
    vision: str = Field(description="High-level vision.")
    tasks: str = Field(description="Actionable tasks.")
    project_name: str = Field(description="Short, punchy project title.")

async def run_scribe_background(thread_id: str):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = await graph.aget_state(config)
        if not state.values: return
        history_text = ""
        for msg in state.values.get("messages", []):
            if isinstance(msg, (HumanMessage, AIMessage)):
                role = "User" if isinstance(msg, HumanMessage) else "Co-Founder"
                content = str(msg.content)
                history_text += f"{role}: {content}\n\n"
        scribe_chain = (ChatPromptTemplate.from_messages([("system", SCRIBE_PROMPT), ("human", "{history}")]) | llm_scribe.with_structured_output(ScribeOutput))
        extraction = await scribe_chain.ainvoke({"history": history_text})
        db.collection("cofounder_boards").document(thread_id).set({"project_name": extraction.project_name, "vision": extraction.vision, "tasks": [{"title": t, "status": "todo"} for t in extraction.tasks.split('\n') if t.strip()], "status": "Active", "updated_at": firestore.SERVER_TIMESTAMP}, merge=True)
    except Exception: pass

# --- 7. API ENDPOINTS ---
app = FastAPI(title="The Co-Founder")

# FIX: Added Port 3001 to CORS and made origins explicit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOUNT ARCHITECT ROUTER ---
app.include_router(architect_router, prefix="/agent/design", tags=["Architect"])

class RenameRequest(BaseModel):
    name: str

class ProfileRequest(BaseModel):
    content: str

@app.post("/agent/thread/{thread_id}/rename")
async def rename_thread(thread_id: str, req: RenameRequest):
    db.collection("cofounder_boards").document(thread_id).update({"project_name": req.name})
    return {"status": "success"}

@app.delete("/agent/thread/{thread_id}")
async def delete_thread(thread_id: str):
    db.collection("cofounder_boards").document(thread_id).delete()
    return {"status": "success"}

@app.get("/agent/profile")
async def get_profile():
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("USER_PROFILE.md")
    return {"content": blob.download_as_text() if blob.exists() else ""}

@app.post("/agent/profile")
async def save_profile(req: ProfileRequest):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("USER_PROFILE.md")
    blob.upload_from_string(req.content)
    return {"status": "success"}

@app.post("/agent/invoke")
async def manual_invoke(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    thread_id = body.get("config", {}).get("configurable", {}).get("thread_id")
    result = await graph.ainvoke(body.get("input", {}), config=body.get("config", {}))
    background_tasks.add_task(run_scribe_background, thread_id)
    return {"output": result}

@app.get("/agent/projects")
async def list_projects():
    docs = db.collection("cofounder_boards").order_by("updated_at", direction=firestore.Query.DESCENDING).limit(50).stream()
    return {"projects": [{"thread_id": d.id, "project_name": d.to_dict().get("project_name", "Untitled"), "updated_at": d.to_dict().get("updated_at").isoformat() if d.to_dict().get("updated_at") else None} for d in docs]}

@app.get("/health")
def health(): return {"status": "IT WORKS"}

add_routes(app, graph, path="/agent_debug")