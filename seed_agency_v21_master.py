import os, firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.client()

DEPARTMENTS = ["the_big_idea", "market_research", "audience_mapping", "user_experience", "the_mvp"]

def seed():
    print("🚀 SEEDING V21: Natural Partner & High-Res Brainstorming")
    
    # 1. THE PROJECT MANAGER
    db.collection("agency_roster").document("master_pm").set({
        "id": "master_pm", "display_name": "Project Manager", "layer_id": "GLOBAL", "dept_id": "HUB",
        "role_index": 0, "model_tier": "FLASH", 
        "system_prompt": """You are a Startup Co-Founder. Be enthusiastic, sharp, and concise. 
        MANDATE: Ask exactly ONE question. Do not provide lists. 
        When the vision is clear, say: 'I have enough info to get the team working, it will take about 1 minute. Shall I get them cracking?'""",
        "optimization_target": "Natural co-authorship."
    })

    # 2. THE STRIKE TEAMS
    for dept in DEPARTMENTS:
        roles = ["visionary", "commercial", "realist"]
        for r in roles:
            agent_id = f"strat_{dept}_{r}"
            db.collection("agency_roster").document(agent_id).set({
                "id": agent_id, "display_name": r.capitalize() + " Architect", "layer_id": "STRATEGY", "dept_id": dept.upper() + "_TEAM",
                "role_index": roles.index(r) + 1, "model_tier": "PRO",
                "system_prompt": f"You are the {r.capitalize()} Architect. Provide 4+ paragraphs of deep Markdown reasoning. Surprise the Director with contrarian insights.",
            })
        
        synth_id = f"strat_{dept}_synthesizer"
        db.collection("agency_roster").document(synth_id).set({
            "id": synth_id, "display_name": "Managing Editor", "layer_id": "STRATEGY", "dept_id": dept.upper() + "_TEAM",
            "role_index": 10, "model_tier": "PRO",
            "system_prompt": "You are the Managing Editor. Adjudicate the debate into a Plain English brief. Fill ALL fields.",
        })

    print("\n🎉 MISSION V21 COMPLETE.")

if __name__ == "__main__":
    seed()