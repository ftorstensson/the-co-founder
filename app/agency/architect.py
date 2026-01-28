# --- SECTION A: IMPORTS & LOGGING ---
import os, json, logging, sys, base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.agency.factory import get_agent_and_dept
from google.cloud import firestore

db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
logger = logging.getLogger("uvicorn.error")
router = APIRouter()

# --- SECTION B: THE STABILIZED DISPATCHER ---
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
        # 1. ANALYZE GATE STATE
        history_list = json.loads(chat_history) if chat_history else []
        user_turns = len([m for m in history_list if m['role'] == 'user'])
        
        is_authoring_request = prompt and any(x in prompt.lower() for x in ["author", "start the paper", "create the paper"])
        is_interview = specialist_id and specialist_id != "null" and specialist_id != ""
        
        # 🛡️ THE HARDENED GATE: Require 3 user turns for Informed Confidence
        is_confident = user_turns >= 3

        # 2. THE DIALOGUE BRANCH
        if not is_authoring_request or is_interview or not is_confident:
            target_id = specialist_id if is_interview else "master_pm"
            
            # If user tries to force authoring too early
            if is_authoring_request and not is_confident:
                logger.info(f"⚠️ [GATE] Authoring blocked. Turns: {user_turns}/3")
                prompt = "The Director is asking for the paper too early. Explain that as a world-class agency, we can't author the 'Big Idea' without 1-2 more clarifying insights. Ask about the business model or the competitive edge."

            logger.info(f"--- ⚡ DISPATCHING ROLE: {target_id} ---")
            agent_config, dept_config = get_agent_and_dept(target_id)
            from app.agency.departments.product.schemas import StrategySpatialOutput
            
            full_instr = f"{agent_config['system_prompt']}\nLens: {dept_config['lens_profile']}\nContext: {strategy_context}"
            messages = [SystemMessage(content=full_instr)]
            
            if chat_history:
                for turn in history_list:
                    role = HumanMessage if turn['role'] == 'user' else AIMessage
                    messages.append(role(content=turn['content']))
            
            if prompt: messages.append(HumanMessage(content=prompt))

            res = agent_config['llm'].with_structured_output(StrategySpatialOutput).invoke(messages)
            raw_result = res.dict()

            if target_id == "master_pm" and raw_result.get("suggested_project_name") and project_id:
                db.collection("cofounder_boards").document(project_id).update({"project_name": raw_result["suggested_project_name"]})
            
            return raw_result

        # 3. THE ASSEMBLY LINE BRANCH (6 Sequential Calls)
        logger.info(f"🏗️  STARTING ASSEMBLY LINE FOR: {prompt}")
        roles = ["RESEARCHER", "ADVOCATE", "LATERAL", "SCOUT", "CONSTRAINT", "SYNTHESIZER"]
        team_results = {}

        for role in roles:
            agent_id = f"strat_big_idea_team_{role.lower()}"
            logger.info(f"   ⚙️  Calling {role} specialist...")
            agent_config, dept_config = get_agent_and_dept(agent_id)
            
            prev_context = json.dumps(team_results, indent=2)
            
            if role != "SYNTHESIZER":
                instr = f"{agent_config['system_prompt']}\nLens: {dept_config['lens_profile']}\nPrevious Findings: {prev_context}"
                # 🛡️ Fix: Ensure HumanMessage is present
                messages = [SystemMessage(content=instr), HumanMessage(content=f"Proceed with deep analysis for the project: {prompt}")]
                res = agent_config['llm'].invoke(messages)
                team_results[role.lower()] = res.content
            else:
                from app.agency.departments.product.schemas import StrategyPaperContent
                final_instr = f"You are the Synthesizer. Turn this debate into a Solution-Oriented Position Paper.\n\nTECHNICAL DEBATE:\n{prev_context}"
                res = agent_config['llm'].with_structured_output(StrategyPaperContent).invoke([SystemMessage(content=final_instr), HumanMessage(content="Write the paper.")])
                
                return {
                    "user_message": "The specialist team has finished the deep-dive. I've adjudicated the tension and published the 'Big Idea' paper to your desk.",
                    "patch": {"dept_id": "the_big_idea", "content": res.dict()},
                    "suggested_project_name": None
                }

    except Exception as e:
        logger.error(f"❌ AGENCY ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))