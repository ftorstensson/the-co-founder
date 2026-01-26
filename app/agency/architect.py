# --- SECTION A: IMPORTS & LOGGING ---
import os, json, logging, sys
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage # <--- Added AIMessage
from app.agency.factory import get_agent_and_dept
from app.agency.departments.product.schemas import StrategySpatialOutput
from google.cloud import firestore

db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
logger = logging.getLogger("uvicorn.error")
router = APIRouter()

# --- SECTION B: THE DISPATCHER (STABILIZED) ---
@router.post("/generate")
async def design_invoke(
    prompt: str = Form(None), 
    layer: str = Form("STRATEGY"), 
    project_id: str = Form(None),
    specialist_id: str = Form(None),
    chat_history: str = Form(None),
    strategy_context: str = Form(None)
):
    try:
        # 1. HIRE THE AGENT
        target_id = specialist_id if (specialist_id and specialist_id != "null") else "master_pm"
        agent_config, dept_config = get_agent_and_dept(target_id)
        
        # 2. CONSTRUCT THE MESSAGE LIST (The Fix)
        # Instead of one big string, we build a chronological list of objects
        messages = [
            SystemMessage(content=f"{agent_config['system_prompt']}\n\n=== REFERENCE CONTEXT (The Desk) ===\n{strategy_context}")
        ]

        # Convert JSON history string into native LangChain Message objects
        if chat_history:
            history_data = json.loads(chat_history)
            for turn in history_data:
                if turn['role'] == 'user':
                    messages.append(HumanMessage(content=turn['content']))
                else:
                    messages.append(AIMessage(content=turn['content']))

        # 3. ADD THE CURRENT INPUT
        if prompt:
            messages.append(HumanMessage(content=prompt))

        # 4. EXECUTION (The Assembly Line logic preserved)
        is_authoring = prompt and ("author" in prompt.lower() or "get the first paper" in prompt.lower())
        
        if not is_authoring or specialist_id:
            # NORMAL DIALOGUE (Using the new message list)
            res = agent_config['llm'].with_structured_output(StrategySpatialOutput).invoke(messages)
            raw_result = res.dict()
            
            # AUTO-NAMING Handshake
            if target_id == "master_pm" and raw_result.get("suggested_project_name") and project_id:
                db.collection("cofounder_boards").document(project_id).update({"project_name": raw_result["suggested_project_name"]})
            
            return raw_result

        # (Assembly Line logic for authoring follows here - omitted for brevity but preserved in your file)
        # ... [Preserve the 6-agent loop from Turn 30 here] ...
        return {"user_message": "Logic for authoring loop continues here..."}

    except Exception as e:
        logger.error(f"❌ DISPATCH ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))