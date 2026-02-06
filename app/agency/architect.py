import os, json, logging
from fastapi import APIRouter, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.agency.factory import get_agent_and_dept
from google.cloud import firestore

# FIXED: Capitalized Client
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
logger = logging.getLogger("uvicorn.error")
router = APIRouter()

@router.post("/generate")
async def design_invoke(
    prompt: str = Form(None), 
    layer: str = Form("STRATEGY"), 
    project_id: str = Form(None),
    specialist_id: str = Form(None),
    chat_history: str = Form(None),
    strategy_context: str = Form(None),
    ambition_dna: str = Form(None)
):
    try:
        history_list = json.loads(chat_history) if chat_history else []
        is_interview = specialist_id and specialist_id != "null" and specialist_id != ""
        
        # 1. THE DIALOGUE PHASE (The Partner PM)
        target_id = specialist_id if is_interview else "master_pm"
        agent_config, dept_config = get_agent_and_dept(target_id)
        from app.agency.departments.product.schemas import StrategySpatialOutput
        
        full_instr = f"{agent_config['system_prompt']}\n\nPROJECT DNA: {ambition_dna}\n\nLens: {dept_config['lens_profile']}\nContext: {strategy_context}"
        messages = [SystemMessage(content=full_instr)]
        
        for turn in history_list:
            role = HumanMessage if turn['role'] == 'user' else AIMessage
            messages.append(role(content=turn['content']))
        if prompt: messages.append(HumanMessage(content=prompt))

        # Invoke the PM (Fast Mode)
        res = agent_config['llm'].with_structured_output(StrategySpatialOutput).invoke(messages)
        pm_decision = res.dict()

        # HANDSHAKE: Auto-Naming turned on for Turn 2+
        if target_id == "master_pm" and pm_decision.get("suggested_project_name") and project_id:
            db.collection("cofounder_boards").document(project_id).update({"project_name": pm_decision["suggested_project_name"]})

        # --- 2. AUTO-PILOT BRIDGE (The "Hire" Logic) ---
        if not is_interview and pm_decision.get("hiring_authorized"):
            target_dept = pm_decision.get("target_dept_id", "the_big_idea")
            logger.info(f"🏗️  AUTO-PILOT: PM hiring strike team for {target_dept}")
            
            roles = ["VISIONARY", "COMMERCIAL", "REALIST", "SYNTHESIZER"]
            team_results = {}
            
            # SNOWBALL HANDOVER: Extract previous paper as a "Primary Constraint"
            ledger = json.loads(strategy_context) if strategy_context else {}
            constraints = ""
            for dept_key, dept_data in ledger.items():
                if dept_data.get('history') and len(dept_data['history']) > 0:
                    prev_paper = dept_data['history'][-1]
                    constraints += f"\n--- INHERITED STRATEGIC ANCHOR ({dept_key}) ---\n{json.dumps(prev_paper['content'])}\n"

            for role in roles:
                agent_id = f"strat_{target_dept.lower()}_{role.lower()}"
                logger.info(f"   ⚔️  Dispatching: {agent_id}")
                s_config, s_lens = get_agent_and_dept(agent_id)
                
                prev_debate = json.dumps(team_results, indent=2)
                
                if role != "SYNTHESIZER":
                    # Deep specialist turn
                    instr = f"{s_config['system_prompt']}\n\nPROJECT DNA: {ambition_dna}\n\nLens: {s_lens['lens_profile']}\n\nPRIMARY CONSTRAINTS:\n{constraints}\n\nDEBATE SO FAR:\n{prev_debate}\n\nMANDATE: Provide deep Markdown analysis (4+ paragraphs). Do not summarize user. Break ground."
                    s_res = s_config['llm'].invoke([SystemMessage(content=instr), HumanMessage(content="Perform your Architect Audit.")])
                    team_results[role.lower()] = s_res.content
                else:
                    # Final Synthesis into a punchy Brief
                    from app.agency.departments.product.schemas import StrategyPaperContent
                    final_instr = f"{s_config['system_prompt']}\n\nTECHNICAL DEBATE:\n{prev_debate}\n\nCONSTRAINTS:\n{constraints}\n\nMANDATE: Adjudicate tension into a 1-page Venture Brief. BANNED: Bullet points."
                    final_res = s_config['llm'].with_structured_output(StrategyPaperContent).invoke([SystemMessage(content=final_instr), HumanMessage(content="Author the Brief.")])
                    
                    return {
                        "user_message": pm_decision["user_message"],
                        "patch": {"dept_id": target_dept, "content": final_res.dict()},
                        "suggested_project_name": pm_decision["suggested_project_name"]
                    }

        return pm_decision

    except Exception as e:
        logger.error(f"❌ AGENCY ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))