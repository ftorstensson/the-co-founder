# PRESERVES: SYS-API, SYS-AI
# UPDATES: SYS-BRN-023 (Model ID Migration for 2026 Stability)

import os
from langchain_google_vertexai import ChatVertexAI

# --- CONFIGURATION ---
REGION = "us-central1"
PROJECT_ID = os.environ.get("GCP_PROJECT", "vibe-agent-final")

def get_specialist(role: str):
    """
    The Hiring Hall: Returns a model configured specifically for a project role.
    Uses IDs confirmed to be available in the 'us-central1' registry.
    """
    
    # 1. THE PROJECT MANAGER (The Face)
    # UPDATED: gemini-2.5-flash is the stable successor to 2.0-flash.
    if role == "PROJECT_MANAGER":
        return ChatVertexAI(
            model_name="gemini-2.5-flash", 
            project=PROJECT_ID,
            location=REGION,
            temperature=0.7, 
            max_output_tokens=1024,
            transport="rest"
        )

    # 2. THE ARCHITECT (The Hands)
    # Target: Gemini 2.5 Pro (Confirmed working in your chain.py)
    if role == "ARCHITECT":
        return ChatVertexAI(
            model_name="gemini-2.5-pro", 
            project=PROJECT_ID,
            location=REGION,
            temperature=0.0, # Zero temp for strict JSON logic
            max_output_tokens=8192,
            transport="rest"
        )

    # DEFAULT FALLBACK
    return ChatVertexAI(
        model_name="gemini-2.5-flash", 
        project=PROJECT_ID, 
        location=REGION, 
        transport="rest"
    )