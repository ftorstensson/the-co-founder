# PRESERVES: SYS-API, SYS-AI
# UPDATES: SYS-BRN-021 (Strict Patch Schema - HARDENED)

from pydantic import BaseModel, Field
from typing import List, Optional

class StrategyPaperContent(BaseModel):
    context: str = Field(description="Executive narrative paragraph (The Soul).")
    summary: List[str] = Field(description="3-5 bold executive takeaways.")
    report: str = Field(description="Full, professional high-density Markdown report.")

class StrategyPatch(BaseModel):
    dept_id: str = Field(description="Registry ID (e.g. product_strategy, growth_lifecycle, audience_research, category_convention).")
    version_note: str = Field(description="What changed in this iteration?")
    content: StrategyPaperContent

class StrategySpatialOutput(BaseModel):
    thought_process: str = Field(description="Internal reasoning (Hidden).")
    user_message: str = Field(description="Direct, warm message to the Director.")
    patch: Optional[StrategyPatch] = Field(default=None, description="ONE department patch per turn. Use None for chat only.")