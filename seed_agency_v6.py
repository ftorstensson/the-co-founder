# --- SECTION A: IMPORTS ---
import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- SECTION B: CONFIG ---
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.client()

# --- SECTION C: THE MATRIX DEFINITION ---
DEPTS = {
    "the_big_idea": "Startup Strategy & Systems Thinking",
    "market_reality": "Market Economics & Intelligence",
    "audience_ecosystem": "Behavioral Psychology & Value Architecture",
    "content_structure": "Information Architecture & SEO/GEO",
    "ux_feasibility": "Interaction Design & Technical Constraints"
}

ROLES = {
    "researcher": "Domain Researcher (Facts & Grounding)",
    "advocate": "Devil’s Advocate (Kill the idea/Find Risks)",
    "lateral": "Lateral Thinker (Reframing & Industry Parallels)",
    "constraint": "Constraint Specialist (Enforce Build Reality)",
    "synthesizer": "Master Synthesizer (Author of the Position Paper)"
}

# --- SECTION D: EXECUTION ---
def seed():
    print("🚀 Purging old Roster and Seeding V6 Lensed Matrix...")
    docs = db.collection("agency_roster").stream()
    for d in docs: d.reference.delete()

    # 1. SEED THE GLOBAL PM
    db.collection("agency_roster").document("master_pm").set({
        "id": "master_pm",
        "display_name": "Project Manager",
        "level_id": "GLOBAL",
        "dept_id": "HUB",
        "role_id": "MANAGER",
        "role": "Social Hub & Partner",
        "model_tier": "FLASH",
        "system_prompt": "You are the Lead Partner. Synthesize specialist tension into A4 Position Papers."
    })

    # 2. SEED THE MATRIX (5x5)
    for dept_id, lens in DEPTS.items():
        for role_id, role_name in ROLES.items():
            agent_id = f"strat_{dept_id}_{role_id}"
            db.collection("agency_roster").document(agent_id).set({
                "id": agent_id,
                "display_name": role_id.capitalize(),
                "level_id": "STRATEGY_DPT",
                "dept_id": dept_id.upper(),
                "role_id": role_id.upper(),
                "role": role_name,
                "lens_profile": lens, # The SME Hat
                "model_tier": "PRO",
                "tools": ["google_search_retrieval"] if role_id == "researcher" else [],
                "system_prompt": f"You are the {role_name}. You look strictly through the lens of {lens}. Find the truths and tensions specific to this domain."
            })
            print(f"✅ Hired: {agent_id}")

    print("\n🎉 V6 Lensed Matrix is Live. 25 Specialists on staff.")

if __name__ == "__main__":
    seed()