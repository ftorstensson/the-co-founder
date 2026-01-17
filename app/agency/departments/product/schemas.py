# --- SECTION A: IMPORTS ---
from pydantic import BaseModel, Field
from typing import List, Optional

# --- SECTION B: THE STRATEGY APPENDIX ---
class StrategyPaperAppendix(BaseModel):
    researcher_notes: str = Field(description="Raw grounding research.")
    devils_advocate_teardown: str = Field(description="Critique of failure modes.")
    outside_thinker_reframing: str = Field(description="Adjacent parallels.")
    rejected_alternatives: List[str] = Field(description="Discarded paths.")
    link_bank: List[str] = Field(description="Clickable URLs.")

# --- SECTION C: THE POSITION CONTENT ---
class StrategyPaperContent(BaseModel):
    masthead: str = Field(description="e.g. THE BIG IDEA")
    headline: str = Field(description="Serif-ready title.")
    context: str = Field(description="The Why.")
    position_narrative: str = Field(description="Justified paragraphs.")
    uncomfortable_truths: List[str] = Field(description="Top 3 hard realities.")
    risky_assumptions: List[str] = Field(description="Assumption risks.")
    appendix: StrategyPaperAppendix

# --- SECTION D: THE FINAL OUTPUT ---
class StrategyPatch(BaseModel):
    dept_id: str = Field(description="ID (e.g. the_big_idea).")
    version_note: str = Field(description="Version history note.")
    content: StrategyPaperContent

class StrategySpatialOutput(BaseModel):
    thought_process: str = Field(description="Internal reasoning.")
    user_message: str = Field(description="Conversation bubble content.")
    suggested_project_name: Optional[str] = Field(default=None, description="Suggest a name if one emerges.")
    patch: Optional[StrategyPatch] = Field(default=None, description="Only provide if authorized to build.")