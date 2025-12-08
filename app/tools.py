import os
from typing import List, Optional
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from google.cloud import firestore
from google.cloud import storage

# Initialize DB
db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))

# Initialize Storage
storage_client = storage.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
BUCKET_NAME = "vibe-agent-user-projects"

def get_bucket():
    return storage_client.bucket(BUCKET_NAME)

@tool
def list_files(thread_id: str, path: str = ".") -> str:
    """
    List files in the project's cloud workspace.
    Args:
        thread_id: The ID of the current conversation/project.
        path: The sub-directory to list (default is root).
    """
    try:
        bucket = get_bucket()
        # GCS uses flat paths, we simulate folders with prefixes
        prefix = f"{thread_id}/{path}/".replace("//", "/")
        if path == ".": prefix = f"{thread_id}/"
        
        blobs = bucket.list_blobs(prefix=prefix)
        file_names = [blob.name.replace(f"{thread_id}/", "") for blob in blobs]
        
        if not file_names:
            return "No files found."
        return "\n".join(sorted(file_names))
    except Exception as e:
        return f"Error listing files: {e}"

@tool
def read_file(thread_id: str, path: str) -> str:
    """
    Read a file from the project's cloud workspace.
    Args:
        thread_id: The ID of the current conversation/project.
        path: The file path (e.g., 'frontend/components/Game.tsx').
    """
    try:
        bucket = get_bucket()
        blob_path = f"{thread_id}/{path}"
        blob = bucket.blob(blob_path)
        
        if not blob.exists():
            return f"Error: File '{path}' does not exist."
            
        content = blob.download_as_text()
        return content[:20000] + ("\n...[truncated]" if len(content) > 20000 else "")
    except Exception as e:
        return f"Error reading {path}: {e}"

@tool
def write_file(thread_id: str, path: str, content: str) -> str:
    """
    Write a file to the project's cloud workspace.
    Args:
        thread_id: The ID of the current conversation/project.
        path: The file path (e.g., 'frontend/components/Game.tsx').
        content: The full code content to write.
    """
    try:
        bucket = get_bucket()
        blob_path = f"{thread_id}/{path}"
        blob = bucket.blob(blob_path)
        
        blob.upload_from_string(content, content_type="text/plain")
        return f"Successfully wrote to {path} in cloud storage."
    except Exception as e:
        return f"Error writing to {path}: {e}"

@tool
def update_board(thread_id: str, phase: str, tasks: List[str], status: str) -> str:
    """
    Updates the visual Project Board for the user.
    Args:
        thread_id: The ID of the current conversation.
        phase: The current phase (e.g., 'Discovery', 'Planning', 'Execution').
        tasks: A list of specific todo items.
        status: A brief status update.
    """
    try:
        doc_ref = db.collection("project_boards").document(thread_id)
        doc_ref.set({
            "phase": phase,
            "tasks": tasks,
            "status": status,
            "updated_at": firestore.SERVER_TIMESTAMP
        }, merge=True)
        return f"Successfully updated Board for thread {thread_id}."
    except Exception as e:
        return f"Error updating board: {e}"

# Export the tools list
inspector_tools = ToolNode([list_files, read_file, write_file, update_board])