import os, firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))

DEPARTMENTS = [
    {"id": "the_big_idea", "label": "The Big Idea"},
    {"id": "market_research", "label": "Market Research"},
    {"id": "audience_mapping", "label": "Audience Mapping"},
    {"id": "user_experience", "label": "User Experience"},
    {"id": "the_mvp", "label": "The MVP - Killer App"}
]

def seed():
    print("🚀 SEEDING V19.1: Natural Partner & High-Res Briefing")
    
    # 1. THE PROJECT MANAGER
    db.collection("agency_roster").document("master_pm").set({
        "id": "master_pm", "display_name": "Project Manager", "layer_id": "GLOBAL", "dept_id": "HUB",
        "role_index": 0, "model_tier": "FLASH", 
        "system_prompt": """You are the Lead Agency Partner. 
        
        PARTNER LAW:
        - NEVER use labels like 'My creative suggestion'. Speak naturally as a co-founder.
        - Use 'We' and 'Our'.
        
        AUTOPILOT TRIGGER:
        When you have enough info (Pain, Magic, Buyer), send this exact message:
        'I have enough info to get the team working, it will take about 1 minute. Sit tight while the architects debate.'
        Then, set 'hiring_authorized' to True.""",
        "optimization_target": "Natural, high-clarity co-authorship.",
        "loss_function": "Punished for robot-jargon or asking multiple questions."
    })

    # 2. THE STRIKE TEAMS
    for dept in DEPARTMENTS:
        roles = [
            {"id": "visionary", "name": "Visionary Architect"},
            {"id": "commercial", "name": "Commercial Architect"},
            {"id": "realist", "name": "Product Realist"}
        ]
        for r in roles:
            agent_id = f"strat_{dept['id']}_{r['id']}"
            db.collection("agency_roster").document(agent_id).set({
                "id": agent_id, "display_name": r["name"], "layer_id": "STRATEGY", "dept_id": dept["id"].upper() + "_TEAM",
                "role_index": roles.index(r) + 1, "model_tier": "PRO",
                "system_prompt": f"You are the {r['name']}. Provide 4+ paragraphs of deep Markdown reasoning. Use ELI Protocol.",
                "optimization_target": "Maximize strategic depth.",
                "loss_function": "Punished for thin logic."
            })
        
        synth_id = f"strat_{dept['id']}_synthesizer"
        db.collection("agency_roster").document(synth_id).set({
            "id": synth_id, "display_name": "Managing Editor", "layer_id": "STRATEGY", "dept_id": dept["id"].upper() + "_TEAM",
            "role_index": 10, "model_tier": "PRO",
            "system_prompt": f"You are the Managing Editor. Adjudicate the Trio debate for {dept['id']}. You MUST fill the specific fields for this paper in the schema. Do not use '...'.",
            "optimization_target": "Produce a high-fidelity directive brief."
        })

    print("\n🎉 MIGRATION COMPLETE.")

if __name__ == "__main__":
    seed()