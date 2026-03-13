# [FUNCTIONAL LEDGER - DO NOT REMOVE]
# 1. [STATE_INGEST]: Atomic load of project manifest.
# 2. [TURN_A_CLERK]: Extract JSON buckets.
# 3. [DOUBLE_LOCK_GATE]: Physics + Permission check.
# 4. [TURN_B_AUTHOR]: Dedicated Prose turn for 2-paragraph verbatim Brief.
# 5. [COMMIT_BRIEF]: Immediate Firestore save of the vision BEFORE research.
# 6. [NATIVE_HOUND]: Native Vertex SDK for URL grounding.
# 7. [STRIKE_TEAM]: Specialists ingest Brief + Raw Buckets + EXOBrain.
# 8. [TRANSPORT_EiC]: Strip [RAW_DATA] tags and preserve markdown links.
# 9. [PERSISTENCE]: Final atomic write of the research results.

# [BANNED PATTERNS]
# - NO POST-RESEARCH SAVES ONLY: The Brief must be saved as soon as it exists.
# - NO MULTI-PART PASSES: Always cast specialist content to str() before Editor.
# - NO AI-FLUFF IN BRIEF: Author turn is restricted to 2 paragraphs of user intent.

import os, json, logging, asyncio, vertexai
from fastapi import APIRouter, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.agency.factory import get_agent_and_dept
from langchain_google_vertexai import ChatVertexAI
from google.cloud import firestore
from vertexai.generative_models import GenerativeModel, Tool
from app.agency.departments.strategy.schemas import (
    StrategySpatialOutput, BigIdeaContent, OpportunityContent, 
    PeopleContent, ExperienceContent, MVPContent, ScribeOutput
)
from app.naming_registry import REGISTRY
from app.guardians.firewall import shield_pm as get_manifesto_display

PROJECT_ID = os.environ.get("GCP_PROJECT", "vibe-agent-final")
vertexai.init(project=PROJECT_ID, location="us-central1")
logger = logging.getLogger("uvicorn.error")
router = APIRouter()
FRONTEND_ROOT = os.environ.get("FRONTEND_PATH", "../vibe-design-lab")
SCHEMA_MAP = {'the_big_idea': BigIdeaContent, 'the_opportunity': OpportunityContent, 'the_people': PeopleContent, 'the_experience': ExperienceContent, 'the_mvp': MVPContent}
db = firestore.Client(project=PROJECT_ID)

@router.post('/generate')
async def design_invoke(prompt: str = Form(None), layer: str = Form('STRATEGY'), project_id: str = Form(None), specialist_id: str = Form(None), chat_history: str = Form(None), strategy_context: str = Form(None)):
    try:
        history_list = json.loads(chat_history) if chat_history else []
        is_interview = bool(specialist_id and specialist_id != 'null' and specialist_id != '')
        
        proj_doc = db.collection('cofounder_boards').document(project_id).get()
        proj_data = proj_doc.to_dict() if proj_doc.exists else {}
        v_man = proj_data.get('vibe_manifest') or {}
        active_manifesto = v_man.get(REGISTRY.MANIFESTO) or {}

        # [TURN_A_CLERK]
        scribe_c, _ = get_agent_and_dept('master_pm')
        scribe_instr = "You are the Librarian (IQ). Verbatim extract facts: core_idea, target_user, founder_frustration, competitor_belief, business_model, success_sentence. Set user_confirmed_start=True ONLY on explicit permission."
        
        scribe_res = scribe_c['llm'].with_structured_output(ScribeOutput).invoke([
            SystemMessage(content=scribe_instr), HumanMessage(content=json.dumps(history_list + [{'role': 'user', 'content': prompt}]))
        ])
        
        if scribe_res:
            active_manifesto.update({k: v for k, v in scribe_res.mission_manifesto.dict().items() if v and k != 'problem_statement'})

        # [DOUBLE_LOCK_GATE]
        req_keys = ['founder_frustration', 'competitor_belief', 'business_model', 'success_sentence']
        missing = [k.replace('_', ' ') for k in req_keys if len(str(active_manifesto.get(k, ""))) < 15]
        physics_open = len(missing) == 0
        permission_open = scribe_res.user_confirmed_start if (scribe_res and physics_open) else False
        hiring_authorized = physics_open and permission_open
        logger.warning(f"[GATE] Physics: {physics_open} | Permission: {permission_open} | Gaps: {missing}")

        strike_result = None
        if (hiring_authorized or is_interview) and not is_interview:
            # [TURN_B_AUTHOR]
            author_res = scribe_c['llm'].invoke([
                SystemMessage(content=f"You are the Author. Write a 2-paragraph summary of the Founder's Intent based on: {json.dumps(active_manifesto)}. Capture the 'Gumboots' detail. No fluff."),
                HumanMessage(content="Write Official Brief.")
            ])
            active_manifesto['problem_statement'] = author_res.content
            
            # [COMMIT_BRIEF]: Save the vision BEFORE the heavy research starts
            v_man[REGISTRY.MANIFESTO] = active_manifesto
            db.collection('cofounder_boards').document(project_id).set({'vibe_manifest': v_man}, merge=True)
            logger.warning("[COMMIT] Brief saved to Firestore.")

            # [NATIVE_HOUND]
            model_hound = GenerativeModel("gemini-2.0-flash-001")
            search_tool = Tool.from_dict({"google_search": {}})
            roles = ['visionary', 'commercial', 'realist']
            team_results, bounty_bank = {}, []
            eli_p = open(os.path.join(FRONTEND_ROOT, "Brain/EXO_BRAINS/GLOBAL/PROTOCOL_ELI.md")).read()

            for role in roles:
                s_c, _ = get_agent_and_dept(f'strat_the_big_idea_{role}')
                h_res = model_hound.generate_content(f"Research 2026 data for: {active_manifesto['problem_statement']}", tools=[search_tool])
                links = [f"[{c.web.title}]({c.web.uri})" for c in getattr(h_res.candidates[0].grounding_metadata, 'grounding_chunks', []) if c.web]
                bounty_bank.extend(links)
                
                # [STR_CASTING]: Force content to string to avoid multi-part 500 errors
                p_instr = f"{s_c['system_prompt']}\n\n[ELI]\n{eli_p}\n\nMISSION:\n{active_manifesto['problem_statement']}\n\nGROUND_TRUTH:\n{json.dumps(active_manifesto)}\n\nLINKS:\n{links}\n\nMANDATE: Cite using [Name](URL) format. No [RAW_DATA] tags."
                p_res = s_c['llm'].invoke([SystemMessage(content=p_instr), HumanMessage(content="Analyze vision. Cite links.")])
                team_results[role] = str(p_res.content) 
                logger.warning(f"[SPECIALIST] {role} finished. Research Density: {len(team_results[role])} chars.")

            e_c, _ = get_agent_and_dept('global_editor')
            editor_instr = f"{e_c['system_prompt']}\n\nCLEANUP: Strip technical tags like [RAW_DATA] or [WEB_DATA]. Ensure links are markdown. DO NOT STRIP URLs.\n\nOFFICIAL_BRIEF: {active_manifesto['problem_statement']}\n\nVISIONARY: {team_results['visionary']}\n\nCOMMERCIAL: {team_results['commercial']}\n\nREALIST: {team_results['realist']}\n\nSOURCES: {' '.join(list(set(bounty_bank)))}"
            strike_result = e_c['llm'].with_structured_output(BigIdeaContent).invoke([SystemMessage(content=editor_instr), HumanMessage(content='Assemble final paper.')])

        # [PM_TURN]
        agent_config, _ = get_agent_and_dept(specialist_id if is_interview else 'master_pm')
        v_prose = get_manifesto_display({'mission_manifesto': active_manifesto})
        
        whisper = getattr(scribe_res, 'whisper', 'Focus on the discovery.')
        law_msg = f"[LIBRARIAN HUD: {whisper}]\n[MISSION STATUS: {'GREEN' if physics_open else 'RED'}]\n\nMANDATE: If RED, address gaps: {missing}. NEVER say team is starting if status is RED."
        
        pm_res = agent_config['llm'].invoke([
            SystemMessage(content=f"IDENTITY: {agent_config['system_prompt']}"),
            SystemMessage(content=law_msg),
            SystemMessage(content=f"CURRENT VISION STATE:\n{v_prose}")
        ] + [(HumanMessage if turn.get('role') == 'user' else AIMessage)(content=turn.get('content', '...')) for turn in history_list] + [HumanMessage(content=prompt)])

        # [PERSISTENCE]: Final result save
        v_man[REGISTRY.MANIFESTO] = active_manifesto
        db.collection('cofounder_boards').document(project_id).set({'vibe_manifest': v_man}, merge=True)
        return {'user_message': pm_res.content, 'suggested_project_name': None, 'manifesto': active_manifesto, 'hiring_authorized': bool(strike_result), 'patch': {'dept_id': 'the_big_idea', 'content': strike_result.dict()} if strike_result else None}
    except Exception as e:
        logger.error(f'❌ AGENCY ERROR: {e}'); import traceback; traceback.print_exc(); raise HTTPException(500, str(e))
