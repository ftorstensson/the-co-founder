# PRESERVES: SYS-API (FastAPI Structure), SYS-AI (Vertex Config)
# UPDATES: SYS-BRN-003 (Rich Sitemap Data)

import os
import base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage

REGION = "us-central1"
PROJECT_ID = os.environ.get("GCP_PROJECT", "vibe-agent-final")

router = APIRouter()

llm_architect = ChatVertexAI(
    model_name="gemini-2.5-flash",
    project=PROJECT_ID,
    location=REGION,
    temperature=0.2,
    max_output_tokens=8192,
)

# --- OUTPUT SCHEMAS ---
class FlowNode(BaseModel):
    id: str
    type: Literal[
        "input", "decision", "output", "default", 
        "page", "group", # Sitemap types
        "MobileScreen", "Header", "Button", "Input", "Image", "Text", "List", "Card"
    ] = Field(description="The component type.")
    
    label: str
    
    # RICH SITEMAP FIELDS
    template: Optional[str] = Field(description="For Sitemaps: 'Feed', 'Dashboard', 'Form', 'Modal', 'Sheet'", default=None)
    content: Optional[List[str]] = Field(description="For Sitemaps: List of 3-5 key content blocks (e.g. 'Hero Image', 'Sign Up Form')", default=None)
    goal: Optional[str] = Field(description="For Sitemaps: The primary user goal (e.g. 'Conversion')", default=None)
    
    parentNode: Optional[str] = Field(description="Parent ID for nested wireframes", default=None)

class FlowEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str = ""

class ArchitectOutput(BaseModel):
    thought_process: str
    nodes: List[FlowNode]
    edges: List[FlowEdge]

# --- PROMPTS ---
PROMPTS = {
    "JOURNEY": """MODE: USER JOURNEY (Logic Flow).
    Output a Flowchart. Nodes are Steps. Edges are Decisions.
    CRITICAL: Use type='decision' for branches, 'input' for start, 'output' for end, 'default' for actions.""",
    
    "SITEMAP": """MODE: CONTENT ARCHITECTURE (Rich Sitemap).
    Output a Tree Diagram of the App Structure.
    
    CRITICAL INSTRUCTIONS:
    1. Use type='page' for every screen/modal.
    2. 'label': The Name (e.g. 'Home').
    3. 'template': The UX Pattern (e.g. 'Feed', 'Map View', 'Bottom Sheet').
    4. 'content': A list of 3-5 HIGH LEVEL items that must exist on this page to tell the story.
    5. 'goal': One short phrase describing the UX goal.
    
    Structure: Top-Down hierarchy.
    Distinguish between full pages and 'Sheet'/'Modal' contexts.""",
    
    "WIREFRAME": """MODE: WIREFRAME (UI Layout).
    1. Create a Container Node (type: 'MobileScreen').
    2. Inside that container, place standard UI components (Header, Button, Input).
    3. Use 'parentNode' to lock components to the screen."""
}

@router.post("/generate")
async def design_invoke(
    prompt: str = Form(None), 
    layer: str = Form("JOURNEY"), 
    file: UploadFile = File(None)
):
    print(f"--- ARCHITECT INVOKED (Layer: {layer}) ---")
    try:
        system_instruction = PROMPTS.get(layer, PROMPTS["JOURNEY"])
        
        messages = [
            SystemMessage(content=f"You are The Architect.\n{system_instruction}\nReturn ONLY JSON matching the schema."),
        ]
        
        content_parts = []
        if prompt: content_parts.append({"type": "text", "text": f"Request: {prompt}"})
        if file:
            audio_bytes = await file.read()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            mime_type = file.content_type or "audio/webm"
            content_parts.append({"type": "media", "mime_type": mime_type, "data": audio_b64})
            content_parts.append({"type": "text", "text": "Analyze the audio command."})

        messages.append(HumanMessage(content=content_parts))

        structured_llm = llm_architect.with_structured_output(ArchitectOutput)
        result = structured_llm.invoke(messages)
        
        return result.dict()

    except Exception as e:
        print(f"ARCHITECT ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))