import os
import uuid
import time
import json
import asyncio
import traceback
from google.cloud import firestore, storage
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any, Literal
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
    
    # --- CONTEXT INJECTION ---
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
    
    # Sanitize History
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

# --- 5. BARE METAL SAVER (WITH FIX) ---
class CustomFirestoreSaver(BaseCheckpointSaver):
    def __init__(self, client: firestore.Client, collection: str = "checkpoints"):
        super().__init__() 
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
        
        checkpoint = load(json.loads(data["checkpoint"]))
        metadata = load(json.loads(data["metadata"]))
        
        return CheckpointTuple({"configurable": {"thread_id": thread_id, "checkpoint_ns": "", "checkpoint_id": data["checkpoint_id"]}}, checkpoint, metadata, None)

    async def aput(self, config, checkpoint, metadata, new_versions):
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"].get("checkpoint_id") or f"{int(time.time()*1000)}_{str(uuid.uuid4())[:8]}"
        
        chk_str = json.dumps(dumpd(checkpoint))
        meta_str = json.dumps(dumpd(metadata))
        
        doc_data = {
            "thread_id": thread_id, 
            "checkpoint_id": checkpoint_id, 
            "checkpoint": chk_str, 
            "metadata": meta_str, 
            "created_at": firestore.SERVER_TIMESTAMP
        }
        await asyncio.to_thread(self.client.collection(self.collection).document(f"{thread_id}_{checkpoint_id}").set, doc_data)
        return {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}
    
    # --- THE FIX: MANDATORY METHOD IMPLEMENTATION ---
    async def aput_writes(self, config, writes, task_id, task_path=""):
        """
        Required by LangGraph v0.2+. 
        For this 'Sidecar' architecture, intermediate writes are transient.
        We drop them to ensure stability.
        """
        # print(f"DEBUG: Dropping writes for {task_id} (Sidecar Mode)")
        pass

    def list(self, config, **kwargs): return []
    async def alist(self, config, **kwargs): return []
    def get_tuple(self, config): return None 
    def put(self, config, checkpoint, metadata, new_versions): return {}

checkpointer = CustomFirestoreSaver(db, "custom_checkpoints")
graph = workflow.compile(checkpointer=checkpointer)

# --- 6. API SETUP ---
app = FastAPI(title="The Co-Founder")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post("/agent/invoke")
async def manual_invoke(request: Request):
    try:
        body = await request.json()
        input_data = body.get("input", {})
        config = body.get("config", {})
        
        if "configurable" not in config or "thread_id" not in config["configurable"]:
            raise HTTPException(status_code=400, detail="Missing thread_id")
            
        print(f"--- INVOKING GRAPH for {config['configurable']['thread_id']} ---")
        result = await graph.ainvoke(input_data, config=config)
        return {"output": result}
    except Exception as e:
        print("!!! ERROR IN MANUAL INVOKE !!!")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

add_routes(app, graph, path="/agent_debug")

# --- 7. SNAPSHOT LOGIC ---
class ScribeOutput(BaseModel):
    vision: str = Field(description="High-level vision.")
    tasks: str = Field(description="Actionable tasks.")
    project_name: str = Field(description="Short, punchy project title.")

@app.post("/agent/snapshot/{thread_id}")
async def snapshot_thread(thread_id: str):
    print(f"--- SNAPSHOT TRIGGERED for {thread_id} ---")
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.aget_state(config)
    if not state.values: return {"status": "No history found"}
    
    history_text = ""
    for msg in state.values.get("messages", []):
        if isinstance(msg, (HumanMessage, AIMessage)):
            role = "User" if isinstance(msg, HumanMessage) else "Co-Founder"
            history_text += f"{role}: {msg.content}\n\n"
            
    scribe_chain = (
        ChatPromptTemplate.from_messages([
            ("system", SCRIBE_PROMPT),
            ("human", "Here is the conversation history:\n\n{history}")
        ]) | llm_scribe.with_structured_output(ScribeOutput)
    )
    
    try:
        extraction = await scribe_chain.ainvoke({"history": history_text})
        update_board.invoke({"thread_id": thread_id, "vision": extraction.vision, "tasks": extraction.tasks, "status": "Active"})
        write_file.invoke({"thread_id": thread_id, "path": "VISION.md", "content": f"# {extraction.project_name}\n\n{extraction.vision}\n\n## Roadmap\n{extraction.tasks}"})
        
        try:
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob("PROJECT_INDEX.md")
            current_index = blob.download_as_text() if blob.exists() else ""
            if extraction.project_name not in current_index:
                new_index = current_index + f"\n**{extraction.project_name}:** {extraction.vision[:50]}... (Status: Active)\n"
                blob.upload_from_string(new_index)
                print(f"✅ Added {extraction.project_name} to Cloud Index")
        except Exception as e: print(f"⚠️ Index Update Error: {e}")
        
        return {"status": "success"}
    except Exception as e:
        print(f"SNAPSHOT FAILED: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/history/{thread_id}")
async def get_history(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        snapshot = await graph.aget_state(config)
        if not snapshot.values: return {"messages": []}
        history = []
        for msg in snapshot.values.get("messages", []):
            if isinstance(msg, (HumanMessage, AIMessage)) and not isinstance(msg, SystemMessage):
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                history.append({"role": role, "content": str(msg.content)})
        return {"messages": history}
    except Exception as e: return {"messages": []}

@app.get("/agent/projects")
async def list_projects():
    try:
        boards_ref = db.collection("cofounder_boards") 
        query = boards_ref.order_by("updated_at", direction=firestore.Query.DESCENDING).limit(50)
        docs = query.stream()
        projects = []
        for doc in docs:
            data = doc.to_dict()
            projects.append({"thread_id": doc.id, "status": data.get("status", "Unknown"), "updated_at": data.get("updated_at").isoformat() if data.get("updated_at") else None})
        return {"projects": projects}
    except Exception: return {"projects": []}

@app.get("/health")
def health(): return {"status": "IT WORKS"}