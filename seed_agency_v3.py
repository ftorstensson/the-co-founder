# --- SECTION A: IMPORTS ---
import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- SECTION B: CONFIG ---
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.client()

# --- SECTION C: HIERARCHICAL ROSTER DATA ---
AGENTS = [
    # LEVEL 0: GLOBAL
    {
        "id": "master_pm",
        "display_name": "Project Manager",
        "level_id": "GLOBAL",
        "dept_id": "hub",
        "role": "Social Hub & Partner",
        "model_tier": "FLASH",
        "system_prompt": "You are the Project Manager. Your partner is the Director."
    },
    # LEVEL 1: STRATEGY -> THE BIG IDEA
    {
        "id": "bi_researcher",
        "display_name": "Domain Researcher",
        "level_id": "STRATEGY",
        "dept_id": "the_big_idea",
        "role": "Factual Grounding",
        "model_tier": "PRO",
        "system_prompt": "You are the Domain Researcher for The Big Idea. Focus on first-principles."
    },
    {
        "id": "bi_advocate",
        "display_name": "Devil's Advocate",
        "level_id": "STRATEGY",
        "dept_id": "the_big_idea",
        "role": "Strategic Tension",
        "model_tier": "PRO",
        "system_prompt": "You are the Devil's Advocate for The Big Idea. Find the failure modes."
    },
    # LEVEL 1: STRATEGY -> MARKET REALITY
    {
        "id": "mr_scout",
        "display_name": "Market Scout",
        "level_id": "STRATEGY",
        "dept_id": "market_reality",
        "role": "Competitive Intelligence",
        "model_tier": "PRO",
        "tools": ["google_search_retrieval"],
        "system_prompt": "You are the Market Scout. Search for real competitors and link banks."
    }
]

# --- SECTION D: EXECUTION ---
def seed():
    print("🚀 Re-Seeding Hierarchical Agency Roster...")
    for agent in AGENTS:
        db.collection("agency_roster").document(agent["id"]).set(agent)
        print(f"✅ Position Filled: {agent['display_name']} in {agent['level_id']} / {agent['dept_id']}")
    print("\n🎉 Agency Org Chart is now Live in Firestore.")

if __name__ == "__main__":
    seed()