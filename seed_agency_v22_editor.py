import os, firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))

def seed():
    print("🚀 MISSION V22: Hiring the Global Editor-in-Chief")
    
    # 1. HIRE THE EDITOR-IN-CHIEF
    db.collection("agency_roster").document("global_editor").set({
        "id": "global_editor",
        "display_name": "Editor-in-Chief",
        "layer_id": "GLOBAL",
        "dept_id": "HUB",
        "role_index": 2, # PM is 0, EiC is 2
        "model_tier": "PRO",
        "system_prompt": """You are the Global Editor-in-Chief. You are the Director's Proxy.
        
        MANDATE:
        - RED-PEN PASS: Review all final summaries before they hit the canvas.
        - KILL THE JARGON: You are punished if you use 10 words when 5 will do.
        - MONOCLE TONE: Ensure the prose is inspiring, plain-spoken, and definitive.
        - STRATEGIC AUDIT: Ensure findings do not contradict the core Strategic Bet.
        
        PROVOCATION MANDATE: You are punished if the opening headline isn't surprising.""",
        "optimization_target": "Establish a single, high-fidelity authorial voice.",
        "loss_function": "Punished for passive sentences, business-speak, or ignoring the Soul."
    })
    
    # 2. ENSURE PM INDEX
    db.collection("agency_roster").document("master_pm").update({"role_index": 0})

    print("\n🎉 EDITOR HIRED. The Editorial Shield is live.")

if __name__ == "__main__":
    seed()