import os
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.client()

DEPTS = [
    {"id": "BIG_IDEA_TEAM", "label": "The Big Idea", "dept_index": 1, "lens_profile": "First-principles and business logic."},
    {"id": "MARKET_TEAM", "label": "Market Reality", "dept_index": 2, "lens_profile": "Economics and competitive intelligence."},
    {"id": "AUDIENCE_TEAM", "label": "Audience & Ecosystem", "dept_index": 3, "lens_profile": "Behavioral psychology and motivation."},
    {"id": "STRUCTURE_TEAM", "label": "Content & Structure", "dept_index": 4, "lens_profile": "IA, SEO, and discoverability."},
    {"id": "FEASIBILITY_TEAM", "label": "UX & Feasibility", "dept_index": 5, "lens_profile": "Technical constraints and MVP logic."}
]

ROLES = [
    {"id": "RESEARCHER", "name": "Domain Researcher", "idx": 1},
    {"id": "ADVOCATE", "name": "Devil's Advocate", "idx": 2},
    {"id": "LATERAL", "name": "Lateral Thinker", "idx": 3},
    {"id": "CONSTRAINT", "name": "Constraint Specialist", "idx": 4},
    {"id": "SYNTHESIZER", "name": "Master Synthesizer", "idx": 5}
]

def seed():
    print("🚀 Purging and Seeding V9 Liquid Agency...")
    for col in ["agency_roster", "department_registry"]:
        docs = db.collection(col).stream()
        for d in docs: d.reference.delete()

    db.collection("agency_roster").document("master_pm").set({
        "id": "master_pm", "display_name": "Project Manager", "level_id": "GLOBAL", "dept_id": "HUB",
        "role_index": 0, "model_tier": "FLASH", "system_prompt": "You are the Project Manager."
    })

    for d in DEPTS:
        db.collection("department_registry").document(d["id"]).set(d)
        for r in ROLES:
            agent_id = f"strat_{d['id'].lower()}_{r['id'].lower()}"
            db.collection("agency_roster").document(agent_id).set({
                "id": agent_id, "display_name": r["name"], "level_id": "STRATEGY_DPT",
                "dept_id": d["id"], "role_index": r["idx"], "model_tier": "PRO",
                "system_prompt": f"You are the {r['name']} for {d['label']}."
            })
    print("🎉 V9 Seeding Successful.")

if __name__ == "__main__":
    seed()