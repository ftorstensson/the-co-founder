import os, logging
from google.cloud import firestore
from langchain_google_vertexai import ChatVertexAI

logger = logging.getLogger("uvicorn.error")
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
REGION = "us-central1"
PROJECT_ID = os.environ.get("GCP_PROJECT", "vibe-agent-final")

def get_agent_and_dept(agent_id: str):
    try:
        a_doc = db.collection("agency_roster").document(agent_id).get()
        a_data = a_doc.to_dict() if a_doc.exists else {"model_tier": "FLASH", "system_prompt": "You are a PM.", "dept_id": "HUB"}
        dept_id = a_data.get("dept_id", "HUB")
        d_doc = db.collection("department_registry").document(dept_id).get()
        d_data = d_doc.to_dict() if d_doc.exists else {"lens_profile": "General strategy."}

        # MODEL SELECTION (Sandbox Aligned)
        tier = a_data.get("model_tier", "FLASH")
        if tier == "PRO": model = "gemini-2.5-pro"
        elif tier == "HOUND": model = "gemini-2.0-flash-001"
        else: model = "gemini-2.5-flash"

        llm = ChatVertexAI(model_name=model, project=PROJECT_ID, location=REGION, transport="rest", temperature=0.1)
        
        if a_data.get("tools") and "google_search_retrieval" in a_data["tools"]:
            try:
                from vertexai.generative_models import Tool
                search_tool = Tool.from_dict({"google_search": {}})
                llm = llm.bind_tools([search_tool])
            except Exception as tool_err:
                logger.error(f"⚠️ [FACTORY] Grounding Bind Failed: {tool_err}")

        global_doc = db.collection("agency_settings").document("global_config").get()
        global_rules = global_doc.to_dict().get("rules", "") if global_doc.exists else ""

        full_dna = f"[GLOBAL PROTOCOLS]\n{global_rules}\n\n[THEORY]\n{a_data.get('exo_brain', '')}\n\n[IDENTITY]\n{a_data.get('system_prompt', '')}\n\n[CONSTRAINTS]\n- TARGET: {a_data.get('optimization_target', '')}\n- LOSS: {a_data.get('loss_function', '')}"
        return {"llm": llm, "system_prompt": full_dna}, d_data
    except Exception as e:
        logger.error(f"❌ [FACTORY] Error: {e}")
        return {"llm": ChatVertexAI(model_name="gemini-2.5-flash"), "system_prompt": "Error."}, {"lens_profile": "Error."}