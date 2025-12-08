import os
from google.cloud import firestore

db = firestore.Client(project="vibe-agent-final")
COLLECTION_NAME = "agent_configs"

# ARCHITECT UPDATE
architect = {
    "id": "technical_architect",
    "name": "The Producer",
    "role": "Planner",
    "system_prompt": """You are the Technical Producer. You create the master_plan.md.\n\nIMPORTANT: All tools (`write_file`, `read_file`, `update_board`) now require a `thread_id`.\n- You MUST extract the `thread_id` from the User input or the Supervisor instruction.\n- Always pass it to the tools.\n\nYOUR JOB:\n1. Receive instructions.\n2. Create/Update `master_plan.md`.\n3. Update the Board.\n4. Report back.""",
    "tools": ["write_file", "read_file", "update_board"],
    "parent_agent": "project_manager"
}

# FRONTEND UPDATE
frontend = {
    "id": "head_of_frontend",
    "name": "Head of Frontend",
    "role": "Executor",
    "system_prompt": """You are the Head of Frontend Engineering.\n\nIMPORTANT: All tools (`write_file`, `read_file`, `list_files`, `update_board`) now require a `thread_id`.\n- You MUST extract the `thread_id` from the instruction.\n- Always pass it to the tools.\n\nCRITICAL DIRECTIVE:\n- You are writing to CLOUD STORAGE, not a local disk.\n- Always use standard paths like `frontend/components/Game.tsx`.\n- The system handles the storage bucket mapping using the `thread_id`.\n\nYOUR PROCESS:\n1. Read `master_plan.md` (pass thread_id).\n2. Update Board status.\n3. Write files (pass thread_id).\n4. Report "Mission Complete".""",
    "tools": ["write_file", "read_file", "list_files", "update_board"],
    "parent_agent": "project_manager"
}

def update_agents():
    print(f"--- Updating Agents for GCS ---")
    doc_ref = db.collection(COLLECTION_NAME).document("technical_architect")
    doc_ref.set(architect)
    doc_ref = db.collection(COLLECTION_NAME).document("head_of_frontend")
    doc_ref.set(frontend)
    print("✅ Agents Re-Trained for Cloud Storage.")

if __name__ == "__main__":
    update_agents()
