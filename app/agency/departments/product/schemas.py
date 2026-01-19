# --- SECTION A: IMPORTS ---
from pydantic import BaseModel, Field
from typing import List, Optional

# --- SECTION B: THE STRATEGY APPENDIX ---
class StrategyPaperAppendix(BaseModel):
    researcher_notes: str = Field(description="Raw domain research and factual grounding (500+ words).")
    devils_advocate_teardown: str = Field(description="Merciless critique of the model's weak points.")
    outside_thinker_reframing: str = Field(description="Non-obvious parallels from adjacent industries.")
    rejected_alternatives: List[str] = Field(description="List of directions considered but discarded.")
    link_bank: List[str] = Field(description="Clickable URLs for competitors and sources.")

# --- SECTION C: THE POSITION CONTENT ---
class StrategyPaperContent(BaseModel):
    masthead: str = Field(description="Label: e.g., THE BIG IDEA")
    headline: str = Field(description="Expressive Serif-ready title.")
    context: str = Field(description="Narrative establishing the project's soul.")
    position_narrative: str = Field(description="Multi-paragraph executive summary. No bullets.")
    uncomfortable_truths: List[str] = Field(description="Top 3 hard realities surfaced by the advocate.")
    risky_assumptions: List[str] = Field(description="1-2 assumptions most likely to break the business.")
    appendix: StrategyPaperAppendix

# --- SECTION D: THE FINAL OUTPUT ---
class StrategyPatch(BaseModel):
    dept_id: str = Field(description="Registry ID (e.g. the_big_idea).")
    version_note: str = Field(description="Description of this version.")
    content: StrategyPaperContent

class StrategySpatialOutput(BaseModel):
    thought_process: str = Field(description="Internal specialist debate (Hidden).")
    user_message: str = Field(description="Direct, warm conversation with the Director.")
    suggested_project_name: Optional[str] = Field(default=None, description="Suggest a 2-3 word project name ONLY when Informed Confidence is reached.")
    patch: Optional[StrategyPatch] = Field(default=None, description="The content update. Provide ONLY when reaching Informed Confidence.")