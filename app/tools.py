import os
from typing import List, Optional
from langchain_core.tools import tool
from google.cloud import firestore
from google.cloud import storage

# Initialize DB
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))

# Initialize Storage
storage_client = storage.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
BUCKET_NAME = "vibe-agent-user-projects"

# --- ISOLATION CONFIGURATION ---
BOARD_COLLECTION = "cofounder_boards" 

def get_bucket():
    return storage_client.bucket(BUCKET_NAME)

@tool
def list_files(thread_id: str, path: str = ".") -> str:
    """List files in the cloud workspace."""
    try:
        bucket = get_bucket()
        prefix = f"{thread_id}/{path}/".replace("//", "/")
        if path == ".": prefix = f"{thread_id}/"
        blobs = bucket.list_blobs(prefix=prefix)
        file_names = [blob.name.replace(f"{thread_id}/", "") for blob in blobs]
        if not file_names: return "No files found."
        return "\n".join(sorted(file_names))
    except Exception as e:
        return f"Error listing files: {e}"

@tool
def read_file(thread_id: str, path: str) -> str:
    """Read a file from cloud workspace."""
    try:
        bucket = get_bucket()
        blob = bucket.blob(f"{thread_id}/{path}")
        if not blob.exists(): return "File not found."
        return blob.download_as_text()
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def write_file(thread_id: str, path: str, content: str) -> str:
    """Write a file to cloud workspace."""
    try:
        print(f"DEBUG: Writing file {path} for {thread_id}")
        bucket = get_bucket()
        blob = bucket.blob(f"{thread_id}/{path}")
        blob.upload_from_string(content, content_type="text/plain")
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def update_board(thread_id: str, vision: str = "", tasks: str = "", status: str = "active") -> str:
    """
    Updates the Knowledge Base (Board) for the user.
    Args:
        thread_id: The ID of the current conversation.
        vision: The high-level vision summary (Markdown allowed).
        tasks: A simple text list of tasks (e.g. "- Task 1\n- Task 2").
        status: Current status (Discovery, Drafting, etc).
    """
    print(f"🔥 DEBUG: CALLING UPDATE_BOARD for {thread_id}") 
    try:
        doc_ref = db.collection(BOARD_COLLECTION).document(thread_id)
        
        formatted_tasks = []
        if tasks:
            for line in tasks.split("\n"):
                clean_line = line.strip().strip("- ").strip("* ")
                if clean_line:
                    formatted_tasks.append({"title": clean_line, "status": "todo"})

        data = {
            "updated_at": firestore.SERVER_TIMESTAMP,
            "status": status
        }
        
        if vision: data["vision"] = vision
        if formatted_tasks: data["tasks"] = formatted_tasks
            
        doc_ref.set(data, merge=True)
        print("✅ DEBUG: Board Updated Successfully")
        return f"Successfully updated Knowledge Base for {thread_id}."
    except Exception as e:
        print(f"❌ DEBUG: Board Update Failed: {e}")
        return f"Error updating board: {e}"