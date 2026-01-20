# --- SECTION A: IMPORTS ---
import os
from google.cloud import firestore
from langchain_google_vertexai import ChatVertexAI

db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
REGION = "us-central1"
PROJECT_ID = os.environ.get("GCP_PROJECT", "vibe-agent-final")

# --- SECTION B: DUAL-COLLECTION RESOLVER ---
def get_agent_and_dept(agent_id: str):
    # 1. Fetch Agent
    a_doc = db.collection("agency_roster").document(agent_id).get()
    a_data = a_doc.to_dict() if a_doc.exists else {"model_tier": "FLASH", "system_prompt": "You are a PM.", "dept_id": "HUB"}
    
    # 2. Fetch Department Lens
    dept_id = a_data.get("dept_id", "HUB")
    d_doc = db.collection("department_registry").document(dept_id).get()
    d_data = d_doc.to_dict() if d_doc.exists else {"lens_profile": "General business strategy."}

    # 3. Initialize Model
    model = "gemini-2.5-pro" if a_data.get("model_tier") == "PRO" else "gemini-2.5-flash"
    llm = ChatVertexAI(model_name=model, project=PROJECT_ID, location=REGION, transport="rest", temperature=0.1)
    
    if a_data.get("tools") and "google_search_retrieval" in a_data["tools"]:
        llm = llm.bind_tools(["google_search_retrieval"])

    return {"llm": llm, "system_prompt": a_data['system_prompt']}, d_data