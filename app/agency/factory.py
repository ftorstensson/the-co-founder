# --- SECTION A: CONFIGURATION ---
import os
from langchain_google_vertexai import ChatVertexAI

REGION = "us-central1"
PROJECT_ID = os.environ.get("GCP_PROJECT", "vibe-agent-final")

# --- SECTION B: THE SPECIALIST REGISTRY ---
def get_specialist(role: str):
    """
    The Hiring Hall: Returns a model configured specifically for a project role.
    Utilizes Gemini 2.5 tracks for production stability.
    """
    
    # 1. THE PROJECT MANAGER (The Face / Editor-in-Chief)
    # Target: Gemini 2.5 Flash for speed and warmth.
    if role == "PROJECT_MANAGER":
        return ChatVertexAI(
            model_name="gemini-2.5-flash", 
            project=PROJECT_ID,
            location=REGION,
            temperature=0.7, 
            max_output_tokens=1024,
            transport="rest"
        )

    # 2. THE RESEARCHER (The Scout / Market Intelligence)
    # Target: Gemini 2.5 Pro + Google Search Grounding.
    # This role creates the Link Bank and performs factual grounding.
    if role == "RESEARCHER":
        return ChatVertexAI(
            model_name="gemini-2.5-pro",
            project=PROJECT_ID,
            location=REGION,
            temperature=0.1, 
            max_output_tokens=4096,
            transport="rest"
        ).bind_tools(["google_search_retrieval"])

    # 3. THE ARCHITECT (The Hands / Structural Author)
    # Target: Gemini 2.5 Pro for high-reasoning JSON and Markdown generation.
    if role == "ARCHITECT":
        return ChatVertexAI(
            model_name="gemini-2.5-pro",
            project=PROJECT_ID,
            location=REGION,
            temperature=0.0, # Zero temperature for strict schema adherence
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