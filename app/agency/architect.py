import os, json, logging, asyncio
from fastapi import APIRouter, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.agency.factory import get_agent_and_dept
from google.cloud import firestore

# FIXED: Capitalized Client for production stability
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
        ledger = json.loads(strategy_context) if strategy_context else {}
        is_interview = specialist_id and specialist_id != "null" and specialist_id != ""

        # --- 1. SEQUENCE GUARD ---
        # Forces the system to build papers in order: 1 -> 2 -> 3 -> 4 -> 5
        ordered_depts = ["the_big_idea", "market_research", "audience_mapping", "user_experience", "the_mvp"]
        next_target = next((d for d in ordered_depts if not ledger.get(d, {}).get('history')), "the_big_idea")

        # --- 2. THE PARTNER PHASE (PM) ---
        target_id = specialist_id if is_interview else "master_pm"
        agent_config, dept_config = get_agent_and_dept(target_id)
        from app.agency.departments.product.schemas import StrategySpatialOutput
        
        full_instr = f"{agent_config['system_prompt']}\n\nPROJECT DNA: {ambition_dna}\n\nLens: {dept_config['lens_profile']}\nContext: {strategy_context}\n\nSTRICT: Do NOT repeat the user. Focus on moving the vision forward."
        messages = [SystemMessage(content=full_instr)]
        
        for turn in history_list:
            role = HumanMessage if turn['role'] == 'user' else AIMessage
            messages.append(role(content=turn['content']))
        
        if prompt: 
            messages.append(HumanMessage(content=prompt))

        # Invoke the PM
        res = agent_config['llm'].with_structured_output(StrategySpatialOutput).invoke(messages)
        pm_decision = res.dict()
        pm_decision["target_dept_id"] = next_target 

        # HANDSHAKE: Auto-Naming logic
        if target_id == "master_pm" and pm_decision.get("suggested_project_name") and project_id:
            db.collection("cofounder_boards").document(project_id).update({"project_name": pm_decision["suggested_project_name"]})

        # --- 3. TWO-STAGE PACING & SPECIALIST FIREWALL ---
        if not is_interview and pm_decision.get("hiring_authorized"):
            
            # Check if we have already given the 1-minute warning in the last turn
            user_said_go = prompt and any(x in prompt.lower() for x in ["go", "yes", "ok", "crack", "make", "create", "start"])
            is_warned = any("1 minute" in m.get('content', '').lower() for m in history_list[-2:])

            if not is_warned and not user_said_go:
                # PM is eager but we must force the permission turn for better UX
                logger.info("🛡️  GATE: Blocking eager hire. Forcing permission turn.")
                pm_decision["hiring_authorized"] = False
                pm_decision["user_message"] = f"I've got the vision for {next_target.replace('_', ' ')}. It'll take about 1 minute for the architects to debate. Shall I get them cracking?"
                return pm_decision

            # Permission exists -> Run Strike Team
            target_dept = pm_decision["target_dept_id"]
            logger.info(f"🏗️  STRIKE TEAM: Commencing deep work for {target_dept}")
            
            roles = ["VISIONARY", "COMMERCIAL", "REALIST", "SYNTHESIZER"]
            team_results = {}
            
            # GATHER CONSTRAINTS: Specialists MUST see previous papers to prevent drift
            constraints = ""
            for d_key, d_data in ledger.items():
                if d_data.get('history'):
                    prev_content = d_data['history'][-1]['content']
                    constraints += f"\n--- ANCHOR: {d_key} ---\n{json.dumps(prev_content)}\n"

            for role in roles:
                agent_id = f"strat_{target_dept}_{role.lower()}"
                s_config, s_lens = get_agent_and_dept(agent_id)
                prev_debate = json.dumps(team_results, indent=2)
                
                await asyncio.sleep(1) # 🛡️ Rate limit protection for Gemini Pro

                if role != "SYNTHESIZER":
                    instr = f"{s_config['system_prompt']}\n\nDNA: {ambition_dna}\n\nANCHORS:\n{constraints}\n\nDEBATE SO FAR:\n{prev_debate}"
                    specialist_msg = f"TASK: Audit the vision '{prompt if prompt else 'The current project'}'. Bring NEW value, do not mirror."
                    s_res = s_config['llm'].invoke([SystemMessage(content=instr), HumanMessage(content=specialist_msg)])
                    team_results[role.lower()] = s_res.content
                else:
                    # Final Synthesis Pass
                    from app.agency.departments.product.schemas import StrategyPaperContent
                    final_instr = f"{s_config['system_prompt']}\n\nTECHNICAL DEBATE:\n{prev_debate}\n\nANCHORS:\n{constraints}\n\nMANDATE: Author the {target_dept} brief. Fill ALL fields. No Jargon."
                    raw_paper = s_config['llm'].with_structured_output(StrategyPaperContent).invoke([SystemMessage(content=final_instr), HumanMessage(content="Finalize the Brief.")])
                    
                    # --- 4. THE EDITORIAL SHIELD (Final Pass) ---
                    logger.info("✍️  EDITORIAL PASS: Global Editor-in-Chief reviewing...")
                    e_config, _ = get_agent_and_dept("global_editor")
                    edit_msg = f"Original Brief Payload:\n{json.dumps(raw_paper.dict())}\n\nAction: Polish for the Director. Kill jargon. Make it inspiring."
                    polished_paper = e_config['llm'].with_structured_output(StrategyPaperContent).invoke([SystemMessage(content=e_config['system_prompt']), HumanMessage(content=edit_msg)])
                    
                    return {
                        "user_message": f"The team has finished. I've adjudicated the tension and the Editor-in-Chief has polished the final brief for {target_dept.replace('_', ' ')}. It's ready on the board.",
                        "patch": {"dept_id": target_dept, "content": polished_paper.dict()},
                        "suggested_project_name": pm_decision["suggested_project_name"]
                    }

        return pm_decision

    except Exception as e:
        logger.error(f"❌ AGENCY ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))