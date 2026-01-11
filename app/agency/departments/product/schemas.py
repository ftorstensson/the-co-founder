# PRESERVES: SYS-API, SYS-AI
# UPDATES: SYS-BRN-016 (Executive Paper Schema)

from pydantic import BaseModel, Field
from typing import List, Optional

class StrategyPaperData(BaseModel):
    id: str = Field(description="Unique ID for the department (e.g., product_strategy, growth_lifecycle)")
    deptId: str = Field(description="The numeric department number (1-9)")
    label: str = Field(description="The formal title of the Position Paper")
    version: str = Field(description="The current document version (e.g., 1.0, 1.1)")
    icon: str = Field(description="Icon key: landscape, audience, loop, vibe, metrics, growth, message, experience, content")
    context: str = Field(description="A high-level narrative paragraph (3-4 sentences) explaining the 'Why' behind this paper.")
    summary: List[str] = Field(description="3-5 punchy, executive-level takeaways for the card view.")
    report: str = Field(description="The full, high-density professional Markdown report for the deep-dive.")

class StrategySpatialOutput(BaseModel):
    thought_process: str = Field(description="Internal specialist debate and strategic reasoning (Hidden from user).")
    user_message: str = Field(description="The PM's social response. Use this to ask clarifying questions or explain which paper was just 'printed'.")
    nodes: Optional[List[StrategyPaperData]] = Field(default=None, description="The list of authored executive papers to render on the canvas.")