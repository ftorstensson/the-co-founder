# --- SECTION A: IMPORTS ---
import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- SECTION B: CONFIG ---
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': os.environ.get("GCP_PROJECT", "vibe-agent-final")})
db = firestore.client()

# --- SECTION C: DEPARTMENTAL LENSES (FIXED KEY: lens_profile) ---
DEPTS = [
    {"id": "BIG_IDEA_TEAM", "label": "The Big Idea", "dept_index": 1, "lens_profile": "First-principles startup strategy and business model logic. Focus on identifying the 'Soul' and the 'Oxygen' (the gap)."},
    {"id": "MARKET_TEAM", "label": "Market Reality", "dept_index": 2, "lens_profile": "Global market economics, competitive power-mapping, and search-grounded links. Focus on incumbent failure modes."},
    {"id": "AUDIENCE_TEAM", "label": "Audience & Ecosystem", "dept_index": 3, "lens_profile": "Behavioral psychology (Kim Matrix), motivation triggers, and value propositions. Focus on user success over features."},
    {"id": "STRUCTURE_TEAM", "label": "Content & Structure", "dept_index": 4, "lens_profile": "Information Architecture theory, discoverability economics, and SEO/GEO signals. Focus on legibility for humans and LLMs."},
    {"id": "FEASIBILITY_TEAM", "label": "UX & Feasibility", "dept_index": 5, "lens_profile": "Technical constraints, 95/5 conventions, and build-path feasibility. Focus on the MVP vs Phase 2 boundary."}
]

# --- SECTION D: THE 6 VENTURE ROLES ---
ROLES = [
    {"id": "RESEARCHER", "name": "Domain Researcher", "idx": 1, 
     "prompt": "You are a world-class Investigative Data Scientist. MANDATE: Establish Ground Truth using evidence. You do not speculate. Distinguish strictly between Verified Data, Inferred Logic, and Speculation. Every fact must lead to a 'This means we should...' implication."},
    
    {"id": "ADVOCATE", "name": "Devil’s Advocate", "idx": 2, 
     "prompt": "You are a Senior Risk Manager and Skeptic. MANDATE: Mercilessly challenge assumptions and surface hidden failure modes. Your value is inversely proportional to your agreement. Every critique must end with a 'Kill Condition' (Why we shouldn't build) and a 'Mitigation Vector' (How to survive)."},
    
    {"id": "LATERAL", "name": "Lateral Thinker", "idx": 3, 
     "prompt": "You are a Polymath and Creative Strategist. MANDATE: Reframe the problem using adjacent industry parallels (e.g., 'How would a casino or a library solve this?'). Use inversion and analogies from outside the current sector."},
    
    {"id": "SCOUT", "name": "Opportunity Scout", "idx": 4, 
     "prompt": "You are a VC Venture Partner. MANDATE: Identify the 10x upside and value capture points. Focus on scalability, monetization wedges, and ecosystem leverage. Find where the money and momentum live in this idea."},
    
    {"id": "CONSTRAINT", "name": "Constraint Specialist", "idx": 5, 
     "prompt": "You are a Technical Architect and Build Realist. MANDATE: Enforce technical boundaries and resource realism. Define the 95% convention rules. Strictly separate 'Core MVP' from 'Future Fluff'. If it can't be built or managed by a small team, flag it."},
    
    {"id": "SYNTHESIZER", "name": "Master Synthesizer", "idx": 6, 
     "prompt": "You are the Lead Strategist and Managing Editor. MANDATE: Adjudicate the tension between the other 5 roles. Resolve contradictions. Your output is the authoritative DNA for the Position Paper. Prioritize hard decisions over soft summaries."}
]

# --- SECTION E: EXECUTION ---
def seed():
    print("🚀 Re-Fixing V12: Synchronizing keys...")
    
    # 1. PURGE OLD DATA
    for col in ["agency_roster", "department_registry"]:
        for d in db.collection(col).stream(): d.reference.delete()

    # 2. SEED GLOBAL PM
    db.collection("agency_roster").document("master_pm").set({
        "id": "master_pm", "display_name": "Project Manager", "level_id": "GLOBAL", "dept_id": "HUB",
        "role_index": 0, "model_tier": "FLASH", 
        "system_prompt": """You are the Meta-Orchestrator and Lead Agency Partner. 
        MANDATE:
        - DISCOVERY GATE: Ask 3-5 sharp questions before authoring.
        - NAMING: Assign a premium working name on Turn 2.
        - TRUTH AUDIT: Detect contradictions in specialist reports.
        - SOCIAL: End every turn with exactly ONE sharp question."""
    })

    # 3. SEED DEPARTMENTS & 30 SPECIALISTS
    for d in DEPTS:
        db.collection("department_registry").document(d["id"]).set(d)
        for r in ROLES:
            agent_id = f"strat_{d['id'].lower()}_{r['id'].lower()}"
            db.collection("agency_roster").document(agent_id).set({
                "id": agent_id,
                "display_name": r["name"],
                "level_id": "STRATEGY_DPT",
                "dept_id": d["id"],
                "role_index": r["idx"],
                "model_tier": "PRO",
                "lens_profile": d["lens_profile"], # FIXED: Match key
                "tools": ["google_search_retrieval"] if r["id"] in ["RESEARCHER", "SCOUT"] else [],
                "system_prompt": r["prompt"]
            })
            print(f"   ✅ Brain Inhabited: {r['name']} ({d['label']})")

    print("\n🎉 MISSION V12 SYNCHRONIZED. Lenses and Roles are now visible.")

if __name__ == "__main__":
    seed()