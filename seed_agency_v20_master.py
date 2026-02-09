import os, firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))

DEPARTMENTS = [
    {"id": "the_big_idea", "label": "The Big Idea", "lens": "Venture Architecture. Focus on the core reason to exist and the 'Strategic Bet'."},
    {"id": "market_research", "label": "Market Research", "lens": "Economic Reality. Focus on competitor weaknesses and distribution moats."},
    {"id": "audience_mapping", "label": "Audience Mapping", "lens": "Human Psychology. Focus on user success and hiring conditions (JTBD)."},
    {"id": "user_experience", "label": "User Experience", "lens": "Engagement Design. Focus on loops, habits, and delight."},
    {"id": "the_mvp", "label": "The MVP - Killer App", "lens": "Execution & Scope. Focus on the irreducible build."}
]

def seed():
    print("🚀 SEEDING V20: Plain English & Context Firewall")
    
    # 1. THE PROJECT MANAGER
    db.collection("agency_roster").document("master_pm").set({
        "id": "master_pm", "display_name": "Project Manager", "layer_id": "GLOBAL", "dept_id": "HUB",
        "role_index": 0, "model_tier": "FLASH", 
        "system_prompt": "You are a Startup Co-Founder. Be enthusiastic, creative, and critical. Ask exactly ONE question. Use 'We'. When ready, send the '1 minute' message and authorized hiring.",
        "optimization_target": "Build a high-energy shared vision."
    })

    # 2. THE STRIKE TEAMS
    for dept in DEPARTMENTS:
        # Update Dept Lens
        db.collection("department_registry").document(dept["id"]).set({
            "id": dept["id"], "label": dept["label"], "lens_profile": dept["lens"]
        })
        
        # Architects
        roles = ["visionary", "commercial", "realist"]
        for r in roles:
            agent_id = f"strat_{dept['id']}_{r}"
            db.collection("agency_roster").document(agent_id).update({
                "system_prompt": f"You are the {r.capitalize()} Architect. MANDATE: 4+ paragraphs of deep logic. Focus strictly on the project described by the Director. Use Plain English.",
                "loss_function": "Punished for jargon, meta-talk about AI, or thin logic."
            })
        
        # Synthesizer (The Plain English Guard)
        synth_id = f"strat_{dept['id']}_synthesizer"
        db.collection("agency_roster").document(synth_id).update({
            "system_prompt": "You are the Managing Editor. MANDATE: Adjudicate the debate into a Venture Brief. Use Plain English. No Jargon. Short sentences. High impact. No meta-talk about the agency.",
            "optimization_target": "Crystal clear strategic directive."
        })

    print("\n🎉 MISSION V20 COMPLETE. The Agency is now grounded and human-legible.")

if __name__ == "__main__":
    seed()