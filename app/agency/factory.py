# --- SECTION A: IMPORTS ---
import os
import logging
from google.cloud import firestore
from langchain_google_vertexai import ChatVertexAI

# --- SECTION B: DB & CONFIG INITIALIZATION ---
# Initialize the logger for ground truth
logger = logging.getLogger("uvicorn.error")

# Firestore Client
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))

REGION = "us-central1"
PROJECT_ID = os.environ.get("GCP_PROJECT", "vibe-agent-final")

# --- SECTION C: THE DYNAMIC SPECIALIST RESOLVER ---
def get_specialist(agent_id: str):
    """
    The Liquid Hiring Hall: 
    Fetches agent configuration from Firestore in real-time.
    This allows us to change prompts in the DB without restarting the server.
    """
    logger.info(f"🔍 [FACTORY] Fetching config for agent: {agent_id}")
    
    try:
        # 1. Fetch Config from the agency_roster collection
        doc_ref = db.collection("agency_roster").document(agent_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            logger.warning(f"⚠️ [FACTORY] Agent '{agent_id}' not found in DB. Falling back to default PM.")
            # Default fallback to Flash PM
            return ChatVertexAI(
                model_name="gemini-2.5-flash", 
                project=PROJECT_ID, 
                location=REGION, 
                transport="rest"
            ), "You are a professional Project Manager. Help the Director build their vision."

        config = doc.to_dict()
        
        # 2. Resolve Model Tier
        # We use Gemini 2.5 Pro for 'PRO' tier and Gemini 2.5 Flash for 'FLASH'
        model_name = "gemini-2.5-pro" if config.get("model_tier") == "PRO" else "gemini-2.5-flash"
        
        # 3. Initialize the Client
        # Note: transport="rest" is preserved for macOS stability
        llm = ChatVertexAI(
            model_name=model_name,
            project=PROJECT_ID,
            location=REGION,
            temperature=0.7 if config.get("model_tier") == "FLASH" else 0.1,
            max_output_tokens=8192,
            transport="rest"
        )

        # 4. Attach Tools (e.g., Google Search Grounding)
        if config.get("tools") and "google_search_retrieval" in config["tools"]:
            logger.info(f"🌐 [FACTORY] Binding Google Search to {agent_id}")
            llm = llm.bind_tools(["google_search_retrieval"])

        # 5. Extract the Prompt
        system_prompt = config.get("system_prompt", "No prompt defined.")

        return llm, system_prompt

    except Exception as e:
        logger.error(f"❌ [FACTORY] Error resolving agent {agent_id}: {e}")
        # Return basic fallback to prevent total crash
        return ChatVertexAI(model_name="gemini-2.5-flash", project=PROJECT_ID, location=REGION, transport="rest"), "Error initializing agent."