import os
import json

path = "app/agency/architect.py"
with open(path, "r") as f:
    content = f.read()

# THE FIX: 
# 1. Correct metadata pathing (Line 124).
# 2. Accumulate URLs in a 'bounty_bank'.
# 3. Pass the 'bounty_bank' to the Synthesizer and Editor.

new_logic = """
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
                    constraints += f"\\n--- ANCHOR: {d_key} ---\\n{json.dumps(prev_content)}\\n"

            for role in roles:
                agent_id = f"strat_{target_dept}_{role.lower()}"
                s_config, s_lens = get_agent_and_dept(agent_id)
                prev_debate = json.dumps(team_results, indent=2)
                await asyncio.sleep(1) 

                if role != "synthesizer":
                    instr = f"{s_config['system_prompt']}\\n\\n[MISSION MANIFESTO]\\n{json.dumps(active_manifesto)}\\n\\nDNA: {ambition_dna}\\n\\nDEBATE SO FAR:\\n{prev_debate}"
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
                    bounty_str = "\\n".join(bounty_bank)
                    final_instr = f"{s_config['system_prompt']}\\n\\n[MISSION MANIFESTO]\\n{json.dumps(active_manifesto)}\\n\\n[VERIFIED SOURCES FOUND]\\n{bounty_str}\\n\\nTECHNICAL DEBATE:\\n{prev_debate}\\n\\nMANDATE: Author the {target_dept} brief. Use the Manifesto for facts and the VERIFIED SOURCES for evidence. You MUST fill every field. Include clickable markdown links from the sources."
                    raw_paper = s_config['llm'].with_structured_output(StrategyPaperContent).invoke([SystemMessage(content=final_instr), HumanMessage(content="Finalize Brief.")])
                    
                    e_config, _ = get_agent_and_dept("global_editor")
                    editor_instr = f"{e_config['system_prompt']}\\n\\n[MISSION MANIFESTO]\\n{json.dumps(active_manifesto)}\\n\\n[VERIFIED SOURCES]\\n{bounty_str}\\n\\nMANDATE: Polish the draft. Ensure it reflects the soul of the Manifesto. SACRED LAW: You must preserve at least 3 clickable markdown links from the VERIFIED SOURCES. If they are missing, add them to the Evidence section. Fill ALL fields."
                    polished_paper = e_config['llm'].with_structured_output(StrategyPaperContent).invoke([SystemMessage(content=editor_instr), HumanMessage(content=json.dumps(raw_paper.dict()))])
                    
                    return {
                        "user_message": f"The team has finished. I've adjudicated the tension and the Editor-in-Chief has polished the final brief for {target_dept.replace('_', ' ')}.",
                        "patch": {"dept_id": target_dept, "content": polished_paper.dict()},
                        "suggested_project_name": suggested_name
                    }
"""

# Find the start of the Strike Team block (around line 105)
prefix = content.split("# Run Strike Team")[0]
# Reconstruct the file with the missing return fallback from previous fix
updated_content = prefix + new_logic + "\n\n        return pm_decision" + content.split("return pm_decision")[-1]

with open(path, "w") as f:
    f.write(updated_content)
print("🚀 architect.py 'Link Lockdown' complete. Intelligence verified.")