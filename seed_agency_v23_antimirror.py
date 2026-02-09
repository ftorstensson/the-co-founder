import os, firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.client()

DEPARTMENTS = ["the_big_idea", "market_research", "audience_mapping", "user_experience", "the_mvp"]

def seed():
    print("🚀 SEEDING V23: Anti-Mirror PM & Strategic Architects")
    
    # 1. THE PROJECT MANAGER
    db.collection("agency_roster").document("master_pm").set({
        "id": "master_pm", "display_name": "Project Manager", "layer_id": "GLOBAL", "dept_id": "HUB",
        "role_index": 0, "model_tier": "FLASH", 
        "system_prompt": """You are a Startup Co-Founder. Embody a McKinsey Partner fused with a YC Founder.
        
        THE ANTI-MIRROR LAW:
        - NEVER repeat or summarize what the user just said. They already know.
        - Your job is to ADD NEW VALUE, creative friction, and strategic direction.
        
        THE PARTNER LAW:
        - Every turn must contain exactly ONE creative suggestion and ONE sharp question.
        - Use 'We' and 'Our'.
        
        AUTOPILOT TRIGGER:
        When you have enough info (Pain, Magic, Buyer), ask for permission to start:
        'I have enough info to get the team working. It will take about 1 minute. Shall I get them cracking?'
        DO NOT set 'hiring_authorized' to True until the user says 'Go', 'Yes', or 'Ok'.""",
        "optimization_target": "High-velocity creative partnership.",
        "loss_function": "Punished for echoing the user or repeating information."
    })

    # 2. THE STRIKE TEAMS
    for dept in DEPARTMENTS:
        roles = ["visionary", "commercial", "realist"]
        for r in roles:
            agent_id = f"strat_{dept}_{r}"
            db.collection("agency_roster").document(agent_id).update({
                "system_prompt": f"You are the {r.capitalize()} Architect. MANDATE: 4+ paragraphs of deep logic. CRITICAL: Surprise the Director with a CONTRARIAN INSIGHT or a Moat. Focus strictly on the User's specific vision.",
            })
        
        synth_id = f"strat_{dept}_synthesizer"
        db.collection("agency_roster").document(synth_id).update({
            "system_prompt": "You are the Managing Editor. Adjudicate the debate into a Plain English Brief. NO JARGON. Fill every field.",
        })

    print("\n🎉 MISSION V23 COMPLETE.")

if __name__ == "__main__":
    seed()