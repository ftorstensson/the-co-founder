# --- SECTION A: IMPORTS ---
import os
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.client()

# --- SECTION B: THE DEPARTMENTAL LENSES (The "What") ---
DEPARTMENTS = [
    {"id": "BIG_IDEA_TEAM", "lens_profile": "First-principles and problem-space mechanics.", "mission": "Define the project soul."},
    {"id": "MARKET_TEAM", "lens_profile": "Market economics and competitive intelligence.", "mission": "Find the oxygen in the market."},
    # ... add others in Firebase UI later
]

# --- SECTION C: THE AGENT ROSTER (The "How") ---
ROLES = [
    {"id": "researcher", "role": "Researcher", "tier": "PRO", "prompt": "Focus on facts and grounding."},
    {"id": "advocate", "role": "Devil's Advocate", "tier": "PRO", "prompt": "Find the hidden risks and failure modes."}
]

def seed():
    print("🚀 Seeding Liquid Agency Registry...")
    for d in DEPARTMENTS:
        db.collection("department_registry").document(d["id"]).set(d)
    
    # Seeding one example team
    for r in ROLES:
        agent_id = f"strat_big_idea_{r['id']}"
        db.collection("agency_roster").document(agent_id).set({
            "id": agent_id,
            "dept_id": "BIG_IDEA_TEAM",
            "model_tier": r["tier"],
            "system_prompt": r["prompt"]
        })
    print("🎉 Liquid Unification Complete.")

if __name__ == "__main__":
    seed()