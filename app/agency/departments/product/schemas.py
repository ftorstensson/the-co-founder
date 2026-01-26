# --- SECTION A: IMPORTS ---
from pydantic import BaseModel, Field
from typing import List, Optional

# --- SECTION B: THE STRATEGY APPENDIX ---
class StrategyPaperAppendix(BaseModel):
    domain_research: str = Field(description="Factual grounding and search-based insights from the Researcher.")
    critical_teardown: str = Field(description="The Devil's Advocate teardown of failure modes and Kill Conditions.")
    lateral_reframing: str = Field(description="Adjacent industry analogies and inversion from the Lateral Thinker.")
    opportunity_scout: str = Field(description="Value capture and monetization logic from the Scout.")
    build_constraints: str = Field(description="Technical boundaries and MVP realism from the Constraint Specialist.")
    synthesis_logic: str = Field(description="The partner-level reasoning behind the final Summary from the Lead Strategist.")
    link_bank: List[str] = Field(default_factory=list, description="Clickable URLs for competitors and references.")

# --- SECTION C: THE POSITION CONTENT ---
class StrategyPaperContent(BaseModel):
    masthead: str = Field(description="Label: e.g. THE BIG IDEA")
    headline: str = Field(description="A premium, Substack-style serif headline (Expressive).")
    context: str = Field(description="A brief, inspirational context paragraph defining the soul.")
    summary_content: str = Field(description="High-impact, solution-oriented executive summary. No bullets. Justified text.")
    uncomfortable_truths: List[str] = Field(description="Top 3 hard realities.")
    risky_assumptions: List[str] = Field(description="1-2 biggest risks.")
    appendix: StrategyPaperAppendix

# --- SECTION D: THE PATCH (Must be defined before Output) ---
class StrategyPatch(BaseModel):
    dept_id: str = Field(description="Registry ID (e.g. the_big_idea).")
    version_note: str = Field(description="Brief history note.")
    content: StrategyPaperContent

# --- SECTION E: THE FINAL OUTPUT ---
class StrategySpatialOutput(BaseModel):
    thought_process: str = Field(description="Internal strategic planning and specialist adjudication.")
    user_message: str = Field(description="Direct, warm conversation bubble for the Director.")
    suggested_project_name: Optional[str] = Field(default=None, description="A 2-3 word project name suggested on Turn 2.")
    patch: Optional[StrategyPatch] = Field(default=None, description="The content update for the canvas.")