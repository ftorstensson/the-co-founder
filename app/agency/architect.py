import os, json, logging, asyncio
from fastapi import APIRouter, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from app.agency.factory import get_agent_and_dept
from google.cloud import firestore

# FIXED: Capitalized Client for production stability
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
logger = logging.getLogger("uvicorn.error")
router = APIRouter()

# THE BRIDGE: Path to your other VS Code environment
FRONTEND_ROOT = os.environ.get("FRONTEND_PATH", "../vibe-design-lab")

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
        ordered_depts = ["the_big_idea", "market_research", "audience_mapping", "user_experience", "the_mvp"]
        next_target = next((d for d in ordered_depts if not ledger.get(d, {}).get('history')), "the_big_idea")

        # --- 2. THE PARTNER PHASE (PM) ---
        target_id = specialist_id if is_interview else "master_pm"
        agent_config, dept_config = get_agent_and_dept(target_id)
        from app.agency.departments.product.schemas import StrategySpatialOutput
        
        # --- V4.4 CONSOLIDATED AUTHORITY HIERARCHY ---
        handbook_path = os.path.join(FRONTEND_ROOT, "Brain/AGENCY_MISSION.md")
        handbook_content = open(handbook_path, "r").read() if os.path.exists(handbook_path) else ""
        proj_doc = db.collection("cofounder_boards").document(project_id).get()
        vibe_data = proj_doc.to_dict() if proj_doc.exists else {}
        vibe_manifest = vibe_data.get("vibe_manifest") if isinstance(vibe_data.get("vibe_manifest"), dict) else {}
        ledger_data = vibe_manifest.get("projectLedger", []) if isinstance(vibe_manifest.get("projectLedger"), list) else []
        manifesto_data = vibe_manifest.get("missionManifesto", {})

        if target_id == "master_pm":
            target_dept_doc = db.collection("department_registry").document(next_target.upper() + "_TEAM").get()
            checklist = target_dept_doc.to_dict().get("checklist", []) if target_dept_doc.exists else []
            full_instr = f"[LEVEL 1: CONSTITUTION]\\n{handbook_content}\\n\\n[LEVEL 2: MISSION MANIFESTO]\\n{json.dumps(manifesto_data)}\\n\\n[LEVEL 3: PROJECT LEDGER]\\n{json.dumps(ledger_data)}\\n\\n[LEVEL 4: ACTIVE MISSION CHECKLIST]\\nPHASE: {next_target}\\nGOAL: Help the Director satisfy these items: {json.dumps(checklist)}\\n\\n[LEVEL 5: PERSONA]\\n{agent_config['system_prompt']}\\n\\nMANDATE: You are in the {next_target} phase. Do NOT move to other layers. Suggest a starting point for the checklist items and end with ONE sharp question."
        else:
            full_instr = f"[LEVEL 1: PROJECT LEDGER (LOCKED TRUTHS)]\\n{json.dumps(ledger_data)}\\n\\n[LEVEL 2: PERSONA]\\n{agent_config['system_prompt']}\\n\\n[MISSION]\\nFocus 100% on the vision: '{prompt}'. Do NOT mention the agency or handbook. Lens: {dept_config['lens_profile']}"
        
        messages = [SystemMessage(content=full_instr)]
        for turn in history_list:
            role = HumanMessage if turn.get('role') == 'user' else AIMessage
            messages.append(role(content=turn.get('content', "...")))
        if prompt: messages.append(HumanMessage(content=prompt))

        # PRIME THE ANCHORS
        prime_vision = history_list[0]['content'] if history_list else prompt
        
        # TURN 1: THE SOCIAL PM (FAST LANE)
        res = agent_config['llm'].with_structured_output(StrategySpatialOutput).invoke(messages)
        pm_decision = res.dict()
        pm_decision["target_dept_id"] = next_target 

        # TURN 2: THE INVISIBLE SCRIBE (SLOW LANE)
        active_manifesto = manifesto_data
        hiring_ready = False
        if target_id == "master_pm":
            target_dept_doc = db.collection("department_registry").document(next_target.upper() + "_TEAM").get()
            checklist = target_dept_doc.to_dict().get("checklist", []) if target_dept_doc.exists else []
            from app.agency.departments.product.schemas import ScribeOutput
            scribe_instr = f"You are the Invisible Scribe. Update the Project State. REQUIREMENTS: {json.dumps(checklist)}. Current State: {json.dumps(manifesto_data)}. MANDATE 1: If the project name is UNTITLED, suggest a premium name. MANDATE 2: If the Director authorized the paper (e.g. 'yes', 'go'), set 'hiring_authorized' to True."
            scribe_res = agent_config['llm'].with_structured_output(ScribeOutput).invoke([SystemMessage(content=scribe_instr), HumanMessage(content=json.dumps(history_list))])
            active_manifesto = scribe_res.mission_manifesto.dict()
            hiring_ready = scribe_res.hiring_authorized
            
            # HANDSHAKE & PERSISTENCE
            updates = {"vibe_manifest.missionManifesto": active_manifesto}
            if scribe_res.suggested_project_name: updates["project_name"] = scribe_res.suggested_project_name
            if scribe_res.new_decisions: updates["vibe_manifest.projectLedger"] = (ledger_data if isinstance(ledger_data, list) else []) + [d.dict() for d in scribe_res.new_decisions]
            db.collection("cofounder_boards").document(project_id).update(updates)

        pm_decision["hiring_authorized"] = hiring_ready

        # --- 3. TWO-STAGE PACING ---
        if not is_interview and pm_decision.get("hiring_authorized"):
            is_warned = any("1 minute" in m.get('content', '').lower() for m in history_list[-2:])
            user_explicit_go = prompt and any(x in prompt.lower() for x in ["make", "create", "start", "go", "yes"])
            
            if not is_warned and not user_explicit_go:
                pm_decision["hiring_authorized"] = False
                msg = pm_decision.get("user_message", "")
                if "ready" not in msg.lower():
                    msg += f"\n\nI've got the soul of the {next_target.replace('_', ' ')}. Shall I unleash the team?"
                pm_decision["user_message"] = msg
                return pm_decision

            
            # Run Strike Team
            target_dept = pm_decision["target_dept_id"]
            suggested_name = scribe_res.suggested_project_name if target_id == "master_pm" else None
            logger.info(f"🏗️  STRIKE TEAM: Starting {target_dept} via Mission Manifesto")
            
            ROSTERS = {
                "the_big_idea": ["visionary", "commercial", "realist", "synthesizer"],
                "market_research": ["scout", "historian", "analyst", "synthesizer"],
                "audience_mapping": ["data", "jtbd", "economist", "synthesizer"],
                "user_experience": ["designer", "modeler", "editor", "synthesizer"],
                "the_mvp": ["analyst", "assassin", "editor", "synthesizer"]
            }
            roles = ROSTERS.get(target_dept, ["visionary", "commercial", "realist", "synthesizer"])
            team_results = {}
            bounty_bank = [] # NEW: To store verified URLs
            
            constraints = ""
            for d_key, d_data in ledger.items():
                history = d_data.get('history', [])
                if history:
                    prev_content = history[-1]
                    constraints += f"\n--- ANCHOR: {d_key} ---\n{json.dumps(prev_content)}\n"

            for role in roles:
                agent_id = f"strat_{target_dept}_{role.lower()}"
                s_config, s_lens = get_agent_and_dept(agent_id)
                prev_debate = json.dumps(team_results, indent=2)
                await asyncio.sleep(1) 

                if role != "synthesizer":
                    instr = f"{s_config['system_prompt']}\n\n[MISSION MANIFESTO]\n{json.dumps(active_manifesto)}\n\nDNA: {ambition_dna}\n\nDEBATE SO FAR:\n{prev_debate}"
                    messages = [SystemMessage(content=instr), HumanMessage(content=f"Perform a high-fidelity audit for {target_dept}. You MUST search Google for real-world metrics, competitors, and URLs from 2025/2026. Use the ELI Protocol.")]
                    
                    s_res = s_config['llm'].invoke(messages)
                    team_results[role] = s_res.content
                    
                    # THE RECEIPT HARVEST
                    meta = s_res.response_metadata.get("grounding_metadata", {})
                    queries = meta.get("webSearchQueries") or meta.get("retrievalQueries", [])
                    chunks = meta.get("groundingChunks", [])
                    
                    if queries: logger.warning(f"🔥 [SEARCH TRUTH] {role} googled: {queries}")
                    if chunks:
                        for chunk in chunks:
                            if chunk.get("web"):
                                url_data = f"[{chunk['web'].get('title')}]({chunk['web'].get('uri')})"
                                if url_data not in bounty_bank: bounty_bank.append(url_data)
                        logger.warning(f"📜 [RECEIPTS] {role} cited {len(chunks)} live sources.")
                else:
                    from app.agency.departments.product.schemas import StrategyPaperContent
                    # INJECT THE BOUNTY BANK: Give the Synthesizer the actual URLs
                    bounty_str = "\n".join(bounty_bank)
                    final_instr = f"{s_config['system_prompt']}\n\n[MISSION MANIFESTO]\n{json.dumps(active_manifesto)}\n\n[VERIFIED SOURCES FOUND]\n{bounty_str}\n\nTECHNICAL DEBATE:\n{prev_debate}\n\nMANDATE: Author the {target_dept} brief. Use the Manifesto for facts and the VERIFIED SOURCES for evidence. You MUST fill every field. Include clickable markdown links from the sources."
                    raw_paper = s_config['llm'].with_structured_output(StrategyPaperContent).invoke([SystemMessage(content=final_instr), HumanMessage(content="Finalize Brief.")])
                    
                    e_config, _ = get_agent_and_dept("global_editor")
                    editor_instr = f"{e_config['system_prompt']}\n\n[MISSION MANIFESTO]\n{json.dumps(active_manifesto)}\n\n[VERIFIED SOURCES]\n{bounty_str}\n\nMANDATE: Polish the draft. Ensure it reflects the soul of the Manifesto. SACRED LAW: You must preserve at least 3 clickable markdown links from the VERIFIED SOURCES. If they are missing, add them to the Evidence section. Fill ALL fields."
                    polished_paper = e_config['llm'].with_structured_output(StrategyPaperContent).invoke([SystemMessage(content=editor_instr), HumanMessage(content=json.dumps(raw_paper.dict()))])
                    
                    return {
                        "user_message": f"The team has finished. I've adjudicated the tension and the Editor-in-Chief has polished the final brief for {target_dept.replace('_', ' ')}.",
                        "patch": {"dept_id": target_dept, "content": polished_paper.dict()},
                        "suggested_project_name": suggested_name
                    }


        return pm_decision

    except Exception as e:
        logger.error(f"❌ AGENCY ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
