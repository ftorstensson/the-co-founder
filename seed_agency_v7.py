# --- SECTION A: IMPORTS ---
import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- SECTION B: CONFIG ---
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.client()

# --- SECTION C: ORDERED MATRIX DEFINITION ---
# The order of this list IS the order in the UI
DEPTS = [
    {"id": "the_big_idea", "name": "Big Idea Department", "lens": "Startup Strategy & Systems Thinking"},
    {"id": "market_reality", "name": "Market Reality Department", "lens": "Market Economics & Intelligence"},
    {"id": "audience_ecosystem", "name": "Audience & Ecosystem Department", "lens": "Behavioral Psychology & Value Architecture"},
    {"id": "content_structure", "name": "Content & Structure Department", "lens": "Information Architecture & SEO/GEO"},
    {"id": "ux_feasibility", "name": "UX & Feasibility Department", "lens": "Interaction Design & Technical Constraints"}
]

# The order of this list IS the internal team structure
ROLES = [
    {"id": "researcher", "name": "Domain Researcher", "desc": "(fact-grounded)"},
    {"id": "advocate", "name": "Devil’s Advocate", "desc": "(kill the idea if needed)"},
    {"id": "lateral", "name": "Lateral Thinker", "desc": "(reframes the problem)"},
    {"id": "constraint", "name": "Constraint Specialist", "desc": "(feasibility lens)"},
    {"id": "synthesizer", "name": "Master Synthesizer", "desc": "(produces the final narrative)"}
]

# --- SECTION D: EXECUTION ---
def seed():
    print("🚀 Purging Roster and Seeding V7 Indexed Matrix...")
    docs = db.collection("agency_roster").stream()
    for d in docs: d.reference.delete()

    # 1. SEED GLOBAL PM (Index 0)
    db.collection("agency_roster").document("master_pm").set({
        "id": "master_pm",
        "display_name": "Project Manager",
        "level_id": "GLOBAL",
        "dept_id": "HUB",
        "sort_index": 0,
        "role_index": 0,
        "role": "Social Hub & Partner",
        "model_tier": "FLASH",
        "system_prompt": "You are the Lead Partner. Synthesize specialist tension into A4 Position Papers."
    })

    # 2. SEED THE MATRIX (5x5) WITH EXPLICIT INDICES
    for d_idx, dept in enumerate(DEPTS):
        for r_idx, role in enumerate(ROLES):
            agent_id = f"strat_{dept['id']}_{role['id']}"
            db.collection("agency_roster").document(agent_id).set({
                "id": agent_id,
                "display_name": role['name'],
                "level_id": "STRATEGY_DPT",
                "dept_id": dept['id'].upper(),
                "dept_name": dept['name'],
                "dept_index": d_idx + 1, # Vertical order of Departments
                "role_index": r_idx + 1, # Vertical order of Agents in Team
                "role": f"{role['name']} {role['desc']}",
                "lens_profile": dept['lens'],
                "model_tier": "PRO",
                "tools": ["google_search_retrieval"] if role['id'] == "researcher" else [],
                "system_prompt": f"You are the {role['name']}. You look strictly through the lens of {dept['lens']}."
            })
            print(f"✅ Hired: {agent_id} [Pos: {d_idx+1}.{r_idx+1}]")

    print("\n🎉 V7 Indexed Matrix is Live.")

if __name__ == "__main__":
    seed()