from pydantic import BaseModel, Field
from typing import List, Optional

# --- SECTION 1: THE APPENDIX (Deep Architectural Reasoning) ---
class StrategyPaperAppendix(BaseModel):
    visionary_logic: str = Field(description="4+ paragraphs of deep Markdown: Future Pull & Narrative Logic.")
    commercial_logic: str = Field(description="4+ paragraphs of deep Markdown: Economic Logic & Value Triggers.")
    realist_logic: str = Field(description="4+ paragraphs of deep Markdown: Buildability & Sacrifices.")
    adversarial_tension: str = Field(description="Detailed teardown of the disagreements between the Trio.")

# --- SECTION 2: THE VENTURE BRIEF (Concise & Impactful) ---
class StrategyPaperContent(BaseModel):
    masthead: str = Field(description="LABEL: e.g. MARKET REALITY BRIEF")
    headline: str = Field(description="A provocative, short, stance-heavy title.")
    
    soul: str = Field(description="MAX 2 SENTENCES: The irreducible 'Magic' of the project.")
    strategic_bet: str = Field(description="ONE SENTENCE: The primary load-bearing assumption.")
    
    commercial_hypotheses: str = Field(description="Venture math logic. Short, punchy sentences.")
    market_wedge: str = Field(description="The situational entry door. No fluff.")
    
    non_goals: List[str] = Field(description="3-5 specific strategic sacrifices.")
    
    # ACTIONABLE DIRECTIVES
    directives_for_market_scouts: str = Field(description="Commands for Dept 2.")
    directives_for_designers: str = Field(description="Commands for Dept 3 & 4.")
    
    appendix: StrategyPaperAppendix

# --- SECTION 3: THE WRAPPERS (PM Decision Wires) ---
class StrategyPatch(BaseModel):
    dept_id: str = Field(description="The registry slot to update (e.g. market_reality).")
    version_note: str = Field(description="Brief history note.")
    content: StrategyPaperContent

class StrategySpatialOutput(BaseModel):
    thought_process: str = Field(description="Internal reasoning for the partner's stance.")
    user_message: str = Field(description="The Partner's response. Suggestion + Question.")
    suggested_project_name: Optional[str] = Field(default=None)
    
    # AUTO-PILOT WIRES (The Trigger Logic)
    hiring_authorized: bool = Field(default=False, description="Set to TRUE to trigger the strike team loop.")
    target_dept_id: str = Field(default="the_big_idea", description="The ID of the dept to be authored (the_big_idea, market_reality, etc).")
    
    patch: Optional[StrategyPatch] = Field(default=None)