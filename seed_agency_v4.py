# --- SECTION A: IMPORTS ---
import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- SECTION B: CONFIG ---
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.client()

# --- SECTION C: THE SKETCH-ALIGNED ROSTER (V4) ---
# Mapping: level_id -> Dept Accordion | dept_id -> Team Accordion
AGENTS = [
    # --- GLOBAL HUB ---
    {
        "id": "master_pm",
        "display_name": "Project Manager",
        "level_id": "GLOBAL",
        "dept_id": "HUB",
        "role": "Social Hub & Partner",
        "model_tier": "FLASH",
        "system_prompt": "You are the Project Manager. Your partner is the Director."
    },
    # --- STRATEGY DPT -> BIG IDEA TEAM ---
    {
        "id": "bi_researcher",
        "display_name": "Domain Researcher",
        "level_id": "STRATEGY_DPT",
        "dept_id": "BIG_IDEA_TEAM",
        "role": "Factual Grounding",
        "model_tier": "PRO",
        "system_prompt": "You are the Domain Researcher for The Big Idea. Focus on first-principles."
    },
    {
        "id": "bi_advocate",
        "display_name": "Devil's Advocate",
        "level_id": "STRATEGY_DPT",
        "dept_id": "BIG_IDEA_TEAM",
        "role": "Strategic Tension",
        "model_tier": "PRO",
        "system_prompt": "You are the Devil's Advocate for The Big Idea. Find the failure modes."
    },
    # --- STRATEGY DPT -> MARKET TEAM ---
    {
        "id": "mr_scout",
        "display_name": "Market Scout",
        "level_id": "STRATEGY_DPT",
        "dept_id": "MARKET_TEAM",
        "role": "Competitive Intelligence",
        "model_tier": "PRO",
        "tools": ["google_search_retrieval"],
        "system_prompt": "You are the Market Scout. Search for real competitors and link banks."
    },
    # --- JOURNEY DPT -> USER FLOW TEAM ---
    {
        "id": "jf_psychologist",
        "display_name": "Behavioral Psychologist",
        "level_id": "JOURNEY_DPT",
        "dept_id": "USER_FLOW_TEAM",
        "role": "Motivation Analysis",
        "model_tier": "PRO",
        "system_prompt": "You are the Psychologist. Map user motivations to flows."
    }
]

# --- SECTION D: EXECUTION ---
def seed():
    print("🚀 Purging old Roster and Seeding V4 Hierarchy...")
    # Delete old records to prevent "UNKNOWN" or "v3" data leakage
    docs = db.collection("agency_roster").stream()
    for d in docs: d.reference.delete()
    
    for agent in AGENTS:
        db.collection("agency_roster").document(agent["id"]).set(agent)
        print(f"✅ Position Filled: {agent['display_name']} -> {agent['level_id']} -> {agent['dept_id']}")
    print("\n🎉 Agency Org Chart is now Live in Firestore.")

if __name__ == "__main__":
    seed()