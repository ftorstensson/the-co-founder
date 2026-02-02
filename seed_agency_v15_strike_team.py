import os
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.client()

DEPTS = [
    {"id": "BIG_IDEA_TEAM", "label": "The Big Idea", "dept_index": 1, "lens_profile": "Venture Architecture and First-Principles Ignition. Focus on collapsing ambiguity and setting vectors."}
]

# THE PRODUCT ARCHITECT TRIO
STRIKE_TEAM = [
    {
        "id": "VISIONARY",
        "target": "Maximize Narrative Power, Future Inevitability, and Asymmetry.",
        "loss": "Punished for feasibility bias, defensive framing, or incremental ideas.",
        "prompt": "You are the Visionary Architect (CPO). Your job is to define the 'Soul' and the 'Strategic Bet'. Do not restate user input. Identify what stops being a decision and becomes a default behavior if we succeed."
    },
    {
        "id": "COMMERCIAL",
        "target": "Maximize Economic Logic, Market Power, and Scalability.",
        "loss": "Punished for hand-wavy revenue, TAM theatre, or 'figuring it out later'.",
        "prompt": "You are the Commercial Lead. Your job is to design the Economic Logic. Focus on Revenue Triggers and Power Sources (moats). Use venture math, not marketing fluff."
    },
    {
        "id": "REALIST",
        "target": "Maximize Buildability, Structural Simplicity, and Time-to-Learning.",
        "loss": "Punished for overengineering, hypothetical edge cases, or tool-driven thinking.",
        "prompt": "You are the Product Realist. Your job is to define Non-Goals and Directives. Enforce strategic discipline. Tell us what we will sacrifice to guarantee success."
    },
    {
        "id": "SYNTHESIZER",
        "target": "Adjudicate strike-team conflict into a stance-heavy Venture Brief.",
        "loss": "Punished for lists, neutrality, or paraphrasing. Failed if paper is passive.",
        "prompt": "You are the Managing Editor. Turn the Strike Team debate into a McKinsey-grade Venture Brief. Force a choice on every section."
    }
]

def seed():
    print("🚀 SEEDING V15: The Product Architect Strike Team (Dept 1)")
    
    # Clear old Big Idea specialists to avoid confusion
    for doc in db.collection("agency_roster").where("dept_id", "==", "BIG_IDEA_TEAM").stream():
        doc.reference.delete()

    # Inhabit Strike Team
    for r in STRIKE_TEAM:
        agent_id = f"strat_big_idea_team_{r['id'].lower()}"
        db.collection("agency_roster").document(agent_id).set({
            "id": agent_id,
            "display_name": r["id"].capitalize(),
            "layer_id": "STRATEGY",
            "dept_id": "BIG_IDEA_TEAM",
            "role_index": STRIKE_TEAM.index(r) + 1,
            "model_tier": "PRO",
            "system_prompt": r["prompt"],
            "optimization_target": r["target"],
            "loss_function": r["loss"],
            "physics_constraints": "No shared context. Bring one brick to the wall. Do not summarize."
        })
        print(f"   ⚔️  Hired: {r['id']}")

    print("\n🎉 MISSION V15 COMPLETE. Strike Team is live.")

if __name__ == "__main__":
    seed()