# app/agency/architect.py
import os, json, logging
from fastapi import APIRouter, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.agency.factory import get_agent_and_dept
from google.cloud import firestore

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
        user_turns = len([m for m in history_list if m['role'] == 'user'])
        
        is_authoring_request = prompt and any(x in prompt.lower() for x in ["author", "start", "create", "brief"])
        is_interview = specialist_id and specialist_id != "null" and specialist_id != ""
        
        # 1. THE DIALOGUE BRANCH (The Proactive Partner PM)
        if not is_authoring_request or is_interview or user_turns < 3:
            target_id = specialist_id if is_interview else "master_pm"
            agent_config, dept_config = get_agent_and_dept(target_id)
            from app.agency.departments.product.schemas import StrategySpatialOutput
            
            full_instr = f"{agent_config['system_prompt']}\n\nPROJECT DNA: {ambition_dna}\n\nLens: {dept_config['lens_profile']}\nContext: {strategy_context}"
            messages = [SystemMessage(content=full_instr)]
            
            for turn in history_list:
                role = HumanMessage if turn['role'] == 'user' else AIMessage
                messages.append(role(content=turn['content']))
            
            if prompt: messages.append(HumanMessage(content=prompt))

            res = agent_config['llm'].with_structured_output(StrategySpatialOutput).invoke(messages)
            raw_result = res.dict()

            if target_id == "master_pm" and raw_result.get("suggested_project_name") and project_id:
                db.collection("cofounder_boards").document(project_id).update({"project_name": raw_result["suggested_project_name"]})
            
            return raw_result

        # 2. THE STRIKE TEAM ASSEMBLY LINE (Dept 1 Special Case)
        logger.info(f"🏗️  STRIKE TEAM INITIALIZED FOR: {prompt}")
        
        # We replace 6 agents with the 3 Product Architects
        roles = ["VISIONARY", "COMMERCIAL", "REALIST", "SYNTHESIZER"]
        team_results = {}

        for role in roles:
            agent_id = f"strat_big_idea_team_{role.lower()}"
            logger.info(f"   ⚔️  Dispatching {role}...")
            agent_config, dept_config = get_agent_and_dept(agent_id)
            
            prev_context = json.dumps(team_results, indent=2)
            
            if role != "SYNTHESIZER":
                # Independent position papers + forced new ideas
                instr = f"{agent_config['system_prompt']}\n\nPROJECT DNA: {ambition_dna}\n\nLens: {dept_config['lens_profile']}\nPrevious Findings: {prev_context}\n\nMANDATE: Do not paraphrase the user. Introduce at least one NEW strategic risk or opportunity."
                res = agent_config['llm'].invoke([SystemMessage(content=instr), HumanMessage(content=f"Draft your Architect Position for: {prompt}")])
                team_results[role.lower()] = res.content
            else:
                # Master Synthesis into Venture Brief
                from app.agency.departments.product.schemas import StrategyPaperContent
                final_instr = f"{agent_config['system_prompt']}\n\nTECHNICAL DEBATE:\n{prev_context}\n\nMANDATE: Adjudicate the conflict. Write a solution-oriented Venture Brief. BANNED: Bullet points and neutrality."
                res = agent_config['llm'].with_structured_output(StrategyPaperContent).invoke([SystemMessage(content=final_instr), HumanMessage(content="Author the Venture Brief.")])
                
                return {
                    "user_message": "The Product Architect Trio has finished the debate. I've adjudicated the tension and published the 'Venture Brief'.",
                    "patch": {"dept_id": "the_big_idea", "content": res.dict()},
                    "suggested_project_name": None
                }

    except Exception as e:
        logger.error(f"❌ AGENCY ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))