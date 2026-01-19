# --- SECTION A: IMPORTS ---
import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- SECTION B: CONFIG ---
# This uses the default credentials from your environment
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={
        'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final"),
    })

db = firestore.client()

# --- SECTION C: THE ROSTER DATA (The 5 Pillars) ---
AGENTS = [
    {
        "id": "master_pm",
        "display_name": "Project Manager",
        "role": "Master Synthesizer & Social Lead",
        "department": "core",
        "model_tier": "FLASH",
        "tools": [],
        "system_prompt": """You are the 'Master Synthesizer' and Project Manager. Your partner is the Human Director.
        1. BRAINSTORM GATE: If chat history < 3 turns, ask probing questions.
        2. ONE QUESTION: End every turn with exactly ONE sharp question.
        3. SYNTHESIS: Resolve specialist tensions into a final A4 Position Paper."""
    },
    {
        "id": "the_big_idea",
        "display_name": "Startup Wizard",
        "role": "Venture Architect",
        "department": "the_big_idea",
        "model_tier": "PRO",
        "tools": [],
        "system_prompt": "You are the Startup Wizard. You focus on first-principles, business models, and the 'Soul' of the idea."
    },
    {
        "id": "market_reality",
        "display_name": "Market Scout",
        "role": "Competitive Intelligence",
        "department": "market_reality",
        "model_tier": "PRO",
        "tools": ["google_search_retrieval"],
        "system_prompt": "You are the Market Scout. Use real-time search to find competitors, links, and market gaps."
    },
    {
        "id": "audience_ecosystem",
        "display_name": "Psychologist",
        "role": "Behavioral Specialist",
        "department": "audience_ecosystem",
        "model_tier": "PRO",
        "tools": [],
        "system_prompt": "You are the Behavioral Psychologist. Map user motivations and buyer types."
    },
    {
        "id": "content_structure",
        "display_name": "Information Architect",
        "role": "IA Strategist",
        "department": "content_structure",
        "model_tier": "PRO",
        "tools": [],
        "system_prompt": "You are the IA Architect. Design the structural requirements and content silos."
    },
    {
        "id": "ux_feasibility",
        "display_name": "Technical Lead",
        "role": "Build Feasibility",
        "department": "ux_feasibility",
        "model_tier": "PRO",
        "tools": [],
        "system_prompt": "You are the Technical Lead. Evaluate build options and the 95/5 design logic."
    }
]

# --- SECTION D: EXECUTION ---
def seed():
    print("🚀 Seeding Agency Roster to Firestore...")
    for agent in AGENTS:
        db.collection("agency_roster").document(agent["id"]).set(agent)
        print(f"✅ Hired: {agent['display_name']} (Dept: {agent['department']})")
    print("\n🎉 Migration Complete. The Agency is now Liquid.")

if __name__ == "__main__":
    seed()