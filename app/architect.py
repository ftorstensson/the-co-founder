# PRESERVES: SYS-API, SYS-AI, SYS-BRN-006
# UPDATES: SYS-BRN-007 (Added Product Department)

import os
import base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage

# --- IMPORT MANAGERS & SCHEMAS ---

# Dept 1: Product (Strategy Doc) - NEW
from app.agency.departments.product.manager import get_product_prompt
from app.agency.departments.product.schemas import StrategyDocOutput

# Dept 2: Strategy (Journey Flow)
from app.agency.departments.strategy.manager import get_strategy_prompt
from app.agency.departments.strategy.schemas import JourneyOutput

# Dept 3: Information (Sitemap)
from app.agency.departments.information.manager import get_ia_prompt
from app.agency.departments.information.schemas import SitemapOutput

# Dept 4: Design (Wireframe)
from app.agency.departments.design.manager import get_design_prompt
from app.agency.departments.design.schemas import WireframeOutput

REGION = "us-central1"
PROJECT_ID = os.environ.get("GCP_PROJECT", "vibe-agent-final")

router = APIRouter()

llm_architect = ChatVertexAI(
    model_name="gemini-2.5-pro",
    project=PROJECT_ID,
    location=REGION,
    temperature=0.2,
    max_output_tokens=8192,
)

@router.post("/generate")
async def design_invoke(
    prompt: str = Form(None), 
    layer: str = Form("JOURNEY"), 
    file: UploadFile = File(None)
):
    print(f"--- ARCHITECT INVOKED (Layer: {layer}) ---")
    
    try:
        # DYNAMIC ROUTING (The "Hiring Hall")
        target_schema = None
        system_instruction = ""

        if layer == "STRATEGY":
            target_schema = StrategyDocOutput
            system_instruction = get_product_prompt()
            
        elif layer == "JOURNEY":
            target_schema = JourneyOutput
            system_instruction = get_strategy_prompt()
            
        elif layer == "SITEMAP":
            target_schema = SitemapOutput
            system_instruction = get_ia_prompt()
            
        elif layer == "WIREFRAME":
            target_schema = WireframeOutput
            system_instruction = get_design_prompt()

        # --- EXECUTION ---
        messages = [SystemMessage(content=system_instruction)]
        
        content_parts = []
        if prompt: content_parts.append({"type": "text", "text": f"Request: {prompt}"})
        if file:
            audio_bytes = await file.read()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            mime_type = file.content_type or "audio/webm"
            content_parts.append({"type": "media", "mime_type": mime_type, "data": audio_b64})
            content_parts.append({"type": "text", "text": "Analyze the audio command."})

        messages.append(HumanMessage(content=content_parts))

        # Enforce Schema
        structured_llm = llm_architect.with_structured_output(target_schema)
        result = structured_llm.invoke(messages)
        
        # Log thoughts
        if hasattr(result, 'thought_process'):
             print(f"🧠 {layer} DEPT THOUGHTS:\n{result.thought_process}")
        
        return result.dict()

    except Exception as e:
        print(f"ARCHITECT ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))