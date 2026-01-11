# --- SECTION A: IMPORTS & LOGGING ---
import os
import base64
import json
import logging
import sys
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agency.dispatcher")
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

# --- SECTION B: DEPT IMPORTS ---
from app.agency.factory import get_specialist
from app.agency.departments.product.manager import get_product_prompt
from app.agency.departments.product.schemas import StrategySpatialOutput
from app.agency.departments.strategy.manager import get_strategy_prompt
from app.agency.departments.strategy.schemas import JourneyOutput
from app.agency.departments.information.manager import get_ia_prompt
from app.agency.departments.information.schemas import SitemapOutput
from app.agency.departments.design.manager import get_design_prompt
from app.agency.departments.design.schemas import WireframeOutput

router = APIRouter()

# --- SECTION C: MOCK ROUTE ---
@router.post("/mock")
async def design_mock():
    logger.info("--- 🧪 MOCK HANDSHAKE DETECTED ---")
    return {
        "thought_process": "DIAGNOSTIC: Handshake successful.",
        "user_message": "Mock Handshake SUCCESSFUL.",
        "nodes": [{"id": "mock-1", "label": "MOCK PAPER", "icon": "landscape", "summary": ["Plumbing: OK"], "report": "# OK"}]
    }

# --- SECTION D: LIVE ROUTE HEADER (UPDATED SIGNATURE) ---
@router.post("/generate")
async def design_invoke(
    prompt: str = Form(None), 
    layer: str = Form("STRATEGY"), 
    file: UploadFile = File(None),
    chat_history: str = Form(None),  # <--- NEW: Memory Support
    strategy_context: str = Form(None),
    journey_context: str = Form(None),
    sitemap_context: str = Form(None)
):
    logger.info(f"\n--- ⚡ AGENCY ACTIVE: {layer} DEPT ---")
    
    try:
        blueprint_agent = get_specialist("ARCHITECT")
        target_schema = None
        system_instruction = ""

        # --- SECTION E: DYNAMIC ROUTING (MEMORY INJECTION) ---
        if layer == "STRATEGY":
            target_schema = StrategySpatialOutput
            # We now pass chat history and current nodes into the PM's brain
            system_instruction = get_product_prompt(strategy_context, chat_history)
            
        elif layer == "JOURNEY":
            target_schema = JourneyOutput
            system_instruction = get_strategy_prompt(strategy_context)
            
        elif layer == "SITEMAP":
            target_schema = SitemapOutput
            system_instruction = get_ia_prompt(strategy_context, journey_context)
            
        elif layer == "WIREFRAME":
            target_schema = WireframeOutput
            system_instruction = get_design_prompt(strategy_context, sitemap_context)

        # --- SECTION F: EXECUTION ---
        messages = [SystemMessage(content=system_instruction)]
        content_parts = []
        if prompt: content_parts.append({"type": "text", "text": f"Director Latest Message: {prompt}"})
        if file:
            audio_bytes = await file.read()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            content_parts.append({"type": "media", "mime_type": "audio/webm", "data": audio_b64})

        messages.append(HumanMessage(content=content_parts))
        structured_llm = blueprint_agent.with_structured_output(target_schema)
        result = structured_llm.invoke(messages)
        
        raw_result = result.dict()
        logger.info(f"\n--- 🟢 RAW OUTPUT CAPTURED ---\n{json.dumps(raw_result, indent=2)}")
        return raw_result

    except Exception as e:
        logger.error(f"❌ AGENCY ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))