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
        
        # 4. 🛡️ 2026 NATIVE GROUNDING BYPASS
        if a_data.get("tools") and "google_search_retrieval" in a_data["tools"]:
            logger.info(f"🌐 [FACTORY] Binding Native Grounding to {agent_id}")
            try:
                from vertexai.generative_models import Tool
                # The 'from_dict' bypass ensures we match the server's 2026 schema
                search_tool = Tool.from_dict({"google_search": {}})
                llm = llm.bind_tools([search_tool])
            except Exception as tool_err:
                logger.error(f"⚠️ [FACTORY] Grounding Bind Failed: {tool_err}")

        # 5. LIQUID BRAIN ASSEMBLY (v1.2)
        # Fetch Global Rules (Research/ELI/Search Protocols)
        global_doc = db.collection("agency_settings").document("global_config").get()
        global_rules = global_doc.to_dict().get("rules", "") if global_doc.exists else ""

        full_dna = f"""[GLOBAL PROTOCOLS]
{global_rules}

[THEORETICAL FOUNDATION (EXO-BRAIN)]
{a_data.get('exo_brain', '')}

[PERSONA TONE & ROLE]
{a_data.get('system_prompt', '')}

[ADVERSARIAL CONSTRAINTS]
- OPTIMIZATION TARGET: {a_data.get('optimization_target', '')}
- LOSS FUNCTION (PUNISHMENTS): {a_data.get('loss_function', '')}
- PHYSICS CONSTRAINTS: {a_data.get('physics_constraints', '')}"""

        return {"llm": llm, "system_prompt": full_dna}, d_data

    except Exception as e:
        logger.error(f"❌ [FACTORY] Critical Error resolving {agent_id}: {e}")
        fallback = ChatVertexAI(model_name="gemini-2.5-flash", project=PROJECT_ID, location=REGION, transport="rest")
        return {"llm": fallback, "system_prompt": "Error initializing agent."}, {"lens_profile": "Error."}

def get_specialist(role: str):
    return get_agent_and_dept(role)