import os
import uuid
import time
import asyncio
import io
import zipfile
from google.cloud import firestore, storage
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Any, Dict, AsyncIterator, Sequence, List
from typing_extensions import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_vertexai import ChatVertexAI, HarmBlockThreshold, HarmCategory
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langserve import add_routes
from pydantic import BaseModel, Field
from app.tools import list_files, read_file, write_file, update_board

from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

# --- 1. INITIALIZATION ---
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
storage_client = storage.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
BUCKET_NAME = "vibe-agent-user-projects"

def get_agent_config(agent_id: str):
    doc = db.collection("agent_configs").document(agent_id).get()
    if doc.exists: return doc.to_dict()
    # Fallback to avoid crash if DB isn't seeded yet
    return {"system_prompt": "You are a helpful AI assistant."}

pm_config = get_agent_config("project_manager")
product_config = get_agent_config("head_of_product")

# --- 2. MODEL SETUP ---
safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
}

REGION = "us-central1"

# Wrapper to prevent AI->AI 500 Errors
class GeminiToolAdapter(ChatVertexAI):
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any):
        sanitized_messages = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                content = f"Tool Output ({msg.name or 'unknown'}): {msg.content}"
                sanitized_messages.append(HumanMessage(content=content))
            elif isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
                sanitized_messages.append(msg)
            else:
                sanitized_messages.append(HumanMessage(content=str(msg.content)))
        return super()._generate(sanitized_messages, stop=stop, run_manager=run_manager, **kwargs)

llm_flash = GeminiToolAdapter(
    model_name="gemini-2.5-flash",
    project=os.environ.get("GCP_PROJECT", "vibe-agent-final"),
    location=REGION,
    temperature=0.1,
    safety_settings=safety_settings,
)

llm_pro = ChatVertexAI(
    model_name="gemini-2.5-pro",
    project=os.environ.get("GCP_PROJECT", "vibe-agent-final"),
    location=REGION,
    temperature=0.5,
    safety_settings=safety_settings,
)

# --- 3. AGENTS ---
product_agent = create_react_agent(
    llm_flash, 
    tools=[write_file, read_file, list_files, update_board], 
    state_modifier=product_config.get("system_prompt")
)

# --- 4. SUPERVISOR ---
class AgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: Literal["supervisor", "head_of_product", "__end__"]

class RoutingDecision(BaseModel):
    reasoning: str = Field(description="Brief thought process.")
    action: Literal["delegate_to_product", "respond_to_user"] = Field(description="Next step.")
    response_content: str = Field(description="Response text.")

supervisor_router = llm_pro.with_structured_output(RoutingDecision)
supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", pm_config.get("system_prompt")),
    MessagesPlaceholder(variable_name="messages"),
])
supervisor = supervisor_prompt | supervisor_router

def sanitize_messages(messages):
    safe = []
    for msg in messages:
        if isinstance(msg, (HumanMessage, AIMessage)):
            safe.append(msg)
        elif hasattr(msg, "content"):
            safe.append(HumanMessage(content=str(msg.content)))
    return safe

def supervisor_node(state: AgentState, config):
    print(f"--- SUPERVISOR NODE (History: {len(state['messages'])}) ---")
    safe_messages = sanitize_messages(state["messages"])
    thread_id = config["configurable"].get("thread_id", "unknown")
    
    decision: RoutingDecision = supervisor.invoke({"messages": safe_messages})
    print(f"--- DECISION: {decision.action} ---")
    
    if decision.action == "delegate_to_product":
        instruction = f"Context Thread ID: {thread_id}. Instruction: {decision.response_content}"
        return {"messages": [HumanMessage(content=instruction, name="Supervisor")], "next": "head_of_product"}
    
    else:
        return {"messages": [AIMessage(content=decision.response_content)], "next": "__end__"}

def product_node(state: AgentState):
    print("--- HEAD OF PRODUCT NODE ---")
    last_msg = state["messages"][-1]
    result = product_agent.invoke({"messages": [last_msg]})
    last_output = result["messages"][-1]
    return {"messages": [HumanMessage(content=f"PRODUCT REPORT:\n{last_output.content}", name="HeadOfProduct")]}

# --- 5. TOPOLOGY ---
workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("head_of_product", product_node)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges("supervisor", lambda s: s.get("next"), {"head_of_product": "head_of_product", "__end__": END})
workflow.add_edge("head_of_product", "supervisor")

# --- 6. CHECKPOINTER (Unchanged from Foundation) ---
class CustomFirestoreSaver(BaseCheckpointSaver):
    def __init__(self, client: firestore.Client, collection: str = "checkpoints"):
        super().__init__(serde=JsonPlusSerializer())
        self.client = client
        self.collection = collection

    def get_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        query = (
            self.client.collection(self.collection)
            .where("thread_id", "==", thread_id)
            .order_by("checkpoint_id", direction=firestore.Query.DESCENDING)
            .limit(1)
        )
        docs = list(query.stream())
        if not docs: return None
        data = docs[0].to_dict()
        checkpoint = self.serde.loads(data["checkpoint"])
        metadata = self.serde.loads(data["metadata"])
        final_config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": data.get("checkpoint_ns", ""),
                "checkpoint_id": data["checkpoint_id"]
            }
        }
        return CheckpointTuple(final_config, checkpoint, metadata, None)

    async def aget_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        return await asyncio.to_thread(self.get_tuple, config)

    def list(self, config: Optional[Dict[str, Any]], *, filter: Optional[Dict[str, Any]] = None, before: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> AsyncIterator[CheckpointTuple]:
        return []

    async def alist(self, config: Optional[Dict[str, Any]], *, filter: Optional[Dict[str, Any]] = None, before: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> AsyncIterator[CheckpointTuple]:
        return []

    async def aput(self, config: Dict[str, Any], checkpoint: Checkpoint, metadata: CheckpointMetadata, new_versions: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        if config["configurable"].get("checkpoint_id"):
             checkpoint_id = config["configurable"]["checkpoint_id"]
        else:
             checkpoint_id = f"{int(time.time()*1000)}_{str(uuid.uuid4())[:8]}"
        
        doc_data = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
            "checkpoint": self.serde.dumps(checkpoint),
            "metadata": self.serde.dumps(metadata),
            "created_at": firestore.SERVER_TIMESTAMP
        }
        doc_ref = self.client.collection(self.collection).document(f"{thread_id}_{checkpoint_id}")
        await asyncio.to_thread(doc_ref.set, doc_data)
        return {"configurable": {"thread_id": thread_id, "checkpoint_ns": checkpoint_ns, "checkpoint_id": checkpoint_id}}

    def put(self, config: Dict[str, Any], checkpoint: Checkpoint, metadata: CheckpointMetadata, new_versions: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {}

checkpointer = CustomFirestoreSaver(db, "custom_checkpoints")
graph = workflow.compile(checkpointer=checkpointer)

app = FastAPI(title="The Co-Founder (Knowledge Engine)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://co-founder-frontend-534939227554.australia-southeast1.run.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_routes(app, graph, path="/agent")

# --- 7. ENDPOINTS (Preserve History/Download) ---
@app.get("/agent/download/{thread_id}")
async def download_project(thread_id: str):
    """Zips the project files from GCS."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=f"{thread_id}/")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        found_files = False
        for blob in blobs:
            found_files = True
            file_path = blob.name.replace(f"{thread_id}/", "")
            file_content = blob.download_as_bytes()
            zip_file.writestr(file_path, file_content)
    if not found_files:
        raise HTTPException(status_code=404, detail="No files found for this project.")
    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename=knowledge-{thread_id[-6:]}.zip"})

@app.get("/agent/projects")
async def list_projects():
    try:
        boards_ref = db.collection("project_boards")
        query = boards_ref.order_by("updated_at", direction=firestore.Query.DESCENDING).limit(50)
        docs = query.stream()
        projects = []
        for doc in docs:
            data = doc.to_dict()
            projects.append({
                "thread_id": doc.id,
                "status": data.get("status", "Unknown"),
                "phase": data.get("phase", "Discovery"),
                "updated_at": data.get("updated_at").isoformat() if data.get("updated_at") else None
            })
        return {"projects": projects}
    except Exception as e:
        print(f"Error listing projects: {e}")
        return {"projects": []}

@app.get("/agent/history/{thread_id}")
async def get_history(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        snapshot = await graph.aget_state(config)
        if not snapshot.values:
            return {"messages": []}
        
        history = []
        for msg in snapshot.values.get("messages", []):
            role = "user"
            if isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, HumanMessage):
                role = "user"
            else:
                continue
            history.append({"role": role, "content": str(msg.content)})
            
        return {"messages": history}
    except Exception as e:
        print(f"Error fetching history: {e}")
        return {"messages": []}

@app.get("/health")
def health(): return {"status": "IT WORKS"}