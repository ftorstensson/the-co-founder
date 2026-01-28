# --- SECTION A: IMPORTS ---
import os
import logging
from google.cloud import firestore
from langchain_google_vertexai import ChatVertexAI

# Initialize Ground Truth Logging
logger = logging.getLogger("uvicorn.error")
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))

REGION = "us-central1"
PROJECT_ID = os.environ.get("GCP_PROJECT", "vibe-agent-final")

# --- SECTION B: DUAL-COLLECTION RESOLVER ---
def get_agent_and_dept(agent_id: str):
    """
    Fetches agent config from Firestore and initializes Gemini with correct tools.
    """
    try:
        # 1. Fetch Agent
        a_doc = db.collection("agency_roster").document(agent_id).get()
        a_data = a_doc.to_dict() if a_doc.exists else {"model_tier": "FLASH", "system_prompt": "You are a PM.", "dept_id": "HUB"}
        
        # 2. Fetch Department Lens
        dept_id = a_data.get("dept_id", "HUB")
        d_doc = db.collection("department_registry").document(dept_id).get()
        d_data = d_doc.to_dict() if d_doc.exists else {"lens_profile": "General strategy."}

        # 3. Initialize Model
        model = "gemini-2.5-pro" if a_data.get("model_tier") == "PRO" else "gemini-2.5-flash"
        llm = ChatVertexAI(
            model_name=model, 
            project=PROJECT_ID, 
            location=REGION, 
            transport="rest", 
            temperature=0.1
        )
        
        # 4. 🛡️ FIX: Use the new 'google_search' key for 2026 GA models
        if a_data.get("tools") and "google_search_retrieval" in a_data["tools"]:
            logger.info(f"🌐 [FACTORY] Binding 'google_search' tool to {agent_id}")
            try:
                # Based on the error message, the key must be exactly 'google_search'
                search_tool = {
                    "google_search": {} 
                }
                llm = llm.bind_tools([search_tool])
            except Exception as tool_err:
                logger.error(f"⚠️ [FACTORY] Failed to bind search tool: {tool_err}. Proceeding without search.")

        return {"llm": llm, "system_prompt": a_data['system_prompt']}, d_data

    except Exception as e:
        logger.error(f"❌ [FACTORY] Critical Error resolving {agent_id}: {e}")
        fallback = ChatVertexAI(model_name="gemini-2.5-flash", project=PROJECT_ID, location=REGION, transport="rest")
        return {"llm": fallback, "system_prompt": "Error initializing agent."}, {"lens_profile": "Error."}

def get_specialist(role: str):
    return get_agent_and_dept(role)