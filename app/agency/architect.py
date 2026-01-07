# PRESERVES: SYS-API, SYS-AI
# UPDATES: SYS-BRN-012 (Diagnostic Mock & Force-Flush Logging)

import os
import base64
import json
import logging
import sys
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage

# Setup "Loud" Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agency.dispatcher")
# Force output to terminal immediately
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

# --- IMPORT AGENCY INFRASTRUCTURE ---
from app.agency.factory import get_specialist
from app.agency.departments.product.manager import get_product_prompt
from app.agency.departments.product.schemas import StrategyDocOutput
from app.agency.departments.strategy.manager import get_strategy_prompt
from app.agency.departments.strategy.schemas import JourneyOutput
from app.agency.departments.information.manager import get_ia_prompt
from app.agency.departments.information.schemas import SitemapOutput
from app.agency.departments.design.manager import get_design_prompt
from app.agency.departments.design.schemas import WireframeOutput

router = APIRouter()

# --- 🧪 THE MOCK ROUTE (Non-breaking Diagnostic) ---
@router.post("/mock")
async def design_mock():
    # We use uvicorn logger to ensure it prints even if buffered
    import logging
    logger = logging.getLogger("uvicorn.error")
    logger.info("--- 🧪 MOCK HANDSHAKE DETECTED ---")
    
    return {
        "thought_process": "DIAGNOSTIC: Handshake successful. Backend is alive.",
        "user_message": "Hello Director! The Mock Handshake is SUCCESSFUL. The plumbing is connected.",
        "strategy_doc": "# 🎯 MOCK STRATEGY\n\nIf you see this, the **Markdown Canvas** is working perfectly."
    }

# --- 🧠 THE REAL ROUTE (With Loud Logs) ---
@router.post("/generate")
async def design_invoke(
    prompt: str = Form(None), 
    layer: str = Form("STRATEGY"), 
    file: UploadFile = File(None),
    strategy_context: str = Form(None),
    journey_context: str = Form(None),
    sitemap_context: str = Form(None)
):
    logger.info(f"\n\n--- ⚡ AGENCY ACTIVE: {layer} DEPT ---")
    
    try:
        blueprint_agent = get_specialist("ARCHITECT")
        target_schema = None
        system_instruction = ""

        if layer == "STRATEGY":
            target_schema = StrategyDocOutput
            system_instruction = get_product_prompt()
        elif layer == "JOURNEY":
            target_schema = JourneyOutput
            system_instruction = get_strategy_prompt(strategy_context)
        elif layer == "SITEMAP":
            target_schema = SitemapOutput
            system_instruction = get_ia_prompt(strategy_context, journey_context)
        elif layer == "WIREFRAME":
            target_schema = WireframeOutput
            system_instruction = get_design_prompt(strategy_context, sitemap_context)

        messages = [SystemMessage(content=system_instruction)]
        
        # Log the prompt to the terminal
        logger.debug(f"Input Prompt: {prompt}")

        content_parts = []
        if prompt: content_parts.append({"type": "text", "text": f"Director Input: {prompt}"})
        if file:
            audio_bytes = await file.read()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            content_parts.append({"type": "media", "mime_type": file.content_type or "audio/webm", "data": audio_b64})

        messages.append(HumanMessage(content=content_parts))

        # EXECUTION
        structured_llm = blueprint_agent.with_structured_output(target_schema)
        result = structured_llm.invoke(messages)
        
        # --- THE LOUD LOG (Verification) ---
        raw_result = result.dict()
        logger.info("\n--- 🟢 RAW LLM OUTPUT CAPTURED ---")
        logger.info(json.dumps(raw_result, indent=2))
        logger.info("--- END RAW OUTPUT ---\n")
        
        return raw_result

    except Exception as e:
        logger.error(f"❌ AGENCY ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))