# --- SECTION A: IMPORTS & LOGGING ---
import os, base64, json, logging, sys
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from google.cloud import firestore
from app.agency.factory import get_specialist
from app.agency.departments.product.schemas import StrategySpatialOutput
from app.agency.departments.strategy.schemas import JourneyOutput
from app.agency.departments.information.schemas import SitemapOutput
from app.agency.departments.design.schemas import WireframeOutput

db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
logger = logging.getLogger("uvicorn.error")
router = APIRouter()

# --- SECTION B: MOCK ROUTE ---
@router.post("/mock")
async def design_mock():
    return {"user_message": "Handshake OK", "patch": None}

# --- SECTION C: THE DISPATCHER ---
@router.post("/generate")
async def design_invoke(
    prompt: str = Form(None), 
    layer: str = Form("STRATEGY"), 
    file: UploadFile = File(None),
    chat_history: str = Form(None),
    project_id: str = Form(None),
    specialist_id: str = Form(None), 
    strategy_context: str = Form(None),
    journey_context: str = Form(None),
    sitemap_context: str = Form(None)
):
    target_id = specialist_id if (specialist_id and specialist_id != "null" and specialist_id != "") else "master_pm"
    logger.info(f"\n--- ⚡ LIQUID DISPATCH: {target_id} ---")
    
    try:
        # 1. ANALYZE CURRENT LEDGER STATE
        ledger = json.loads(strategy_context) if strategy_context else {}
        # If 'the_big_idea' hasn't started, we are in the Discovery Loop
        is_discovery = ledger.get('the_big_idea', {}).get('status') == 'NOT_STARTED'
        
        # 2. HIRE SPECIALIST
        agent_llm, system_prompt = get_specialist(target_id)
        
        # 3. CONTEXT INJECTION (Informed Confidence Hint)
        phase_hint = "PHASE: DISCOVERY. Objective: Reach 'Informed Confidence' (The Pain, The Magic, The Buyer)." if is_discovery else "PHASE: EVOLUTION. Objective: Refine or Advance."
        
        full_instruction = f"""
        {system_prompt}

        --- AGENCY STATUS ---
        {phase_hint}
        PROJECT_ID: {project_id}
        """

        messages = [SystemMessage(content=full_instruction)]
        if chat_history:
             messages.append(SystemMessage(content=f"PREVIOUS CONVERSATION: {chat_history}"))
        
        if prompt: 
             messages.append(HumanMessage(content=[{"type": "text", "text": f"Director Turn Input: {prompt}"}]))

        structured_llm = agent_llm.with_structured_output(StrategySpatialOutput if layer == "STRATEGY" else JourneyOutput)
        result = structured_llm.invoke(messages)
        
        if result is None: return {"user_message": "Handshake failed.", "patch": None}
        
        raw_result = result.dict()

        # 4. AUTO-NAMING HANDSHAKE
        if target_id == "master_pm" and raw_result.get("suggested_project_name"):
            new_name = raw_result["suggested_project_name"]
            logger.info(f"🏷️  NAMING: {new_name}")
            db.collection("cofounder_boards").document(project_id).update({"project_name": new_name})

        return raw_result

    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))