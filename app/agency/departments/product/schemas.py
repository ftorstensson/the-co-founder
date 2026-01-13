# PRESERVES: SYS-API, SYS-AI
# UPDATES: SYS-BRN-021 (Strict Patch Schema)

from pydantic import BaseModel, Field
from typing import List, Optional

class StrategyPaperContent(BaseModel):
    context: str = Field(description="Narrative establishing the project's soul.")
    summary: List[str] = Field(description="3-5 executive takeaways.")
    report: str = Field(description="Full high-density Markdown report.")

class StrategyPatch(BaseModel):
    dept_id: str = Field(description="ID from registry (e.g. product_strategy).")
    version_note: str = Field(description="What changed?")
    content: StrategyPaperContent

class StrategySpatialOutput(BaseModel):
    thought_process: str = Field(description="Internal reasoning (Hidden).")
    user_message: str = Field(description="Direct message to the Director.")
    patch: Optional[StrategyPatch] = Field(default=None)