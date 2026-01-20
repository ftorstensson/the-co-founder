# --- SECTION A: IMPORTS ---
import os, base64, json, logging, sys
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from google.cloud import firestore
from app.agency.factory import get_agent_and_dept # <--- Updated logic

db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
logger = logging.getLogger("uvicorn.error")
router = APIRouter()

# --- SECTION B: THE DISPATCHER ---
@router.post("/generate")
async def design_invoke(
    prompt: str = Form(None), 
    layer: str = Form("STRATEGY"), 
    project_id: str = Form(None),
    specialist_id: str = Form(None), 
    chat_history: str = Form(None),
    strategy_context: str = Form(None)
):
    target_id = specialist_id if (specialist_id and specialist_id != "null" and specialist_id != "") else "master_pm"
    
    try:
        # 1. FETCH AGENT + DEPT LENS FROM FIRESTORE
        agent_config, dept_config = get_agent_and_dept(target_id)
        
        # 2. RESOLVE SCHEMA
        from app.agency.departments.product.schemas import StrategySpatialOutput
        target_schema = StrategySpatialOutput # Default for Strategy layer

        # 3. BUILD THE TRIPLE-LOCK PROMPT
        from app.agency.departments.product.manager import get_product_prompt
        
        full_instruction = get_product_prompt(
            agent_prompt=agent_config['system_prompt'],
            dept_lens=dept_config['lens_profile'],
            strategy_context=strategy_context,
            chat_history=chat_history
        )

        messages = [SystemMessage(content=full_instruction)]
        if prompt: 
            messages.append(HumanMessage(content=[{"type": "text", "text": f"turn_input: {prompt}"}]))

        # 4. EXECUTION
        agent_llm = agent_config['llm']
        structured_llm = agent_llm.with_structured_output(target_schema)
        result = structured_llm.invoke(messages)
        
        if result is None: return {"user_message": "Strategic stall.", "patch": None}
        
        raw_result = result.dict()

        # 5. AUTO-NAMING HANDSHAKE
        if target_id == "master_pm" and raw_result.get("suggested_project_name"):
            if project_id:
                db.collection("cofounder_boards").document(project_id).update({"project_name": raw_result["suggested_project_name"]})

        return raw_result

    except Exception as e:
        logger.error(f"❌ DISPATCH ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))