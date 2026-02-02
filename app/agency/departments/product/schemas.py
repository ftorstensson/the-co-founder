from pydantic import BaseModel, Field
from typing import List, Optional

# --- SECTION 1: THE APPENDIX (Architectural Reasoning) ---
class StrategyPaperAppendix(BaseModel):
    visionary_logic: str = Field(description="Narrative Power & Future Inevitability logic.")
    commercial_logic: str = Field(description="Economic Logic, Value Triggers, and Power Sources.")
    realist_logic: str = Field(description="Buildability and sacrificial strategic discipline.")
    adversarial_tension: str = Field(description="Key points of disagreement between the Trio.")

# --- SECTION 2: THE VENTURE BRIEF CONTENT ---
class StrategyPaperContent(BaseModel):
    masthead: str = Field(description="LABEL: THE VENTURE BRIEF")
    headline: str = Field(description="A provocative, stance-heavy title.")
    
    soul: str = Field(description="The irreducible 'Magic'—a concrete claim about the world after this exists.")
    strategic_bet: str = Field(description="The primary load-bearing assumption: 'We believe X because Y, despite Z'.")
    
    commercial_hypotheses: str = Field(description="Revenue Triggers and Value Metrics. Venture math, not marketing.")
    market_wedge: str = Field(description="The Situational 'Hiring Condition' (JTBD) and the Entry Door.")
    
    non_goals: List[str] = Field(description="3-5 strategic sacrifices (What we will NOT build to ensure success).")
    
    # ACTIONABLE DIRECTIVES
    directives_for_market_scouts: str = Field(description="Orders for Dept 2 (Market Reality).")
    directives_for_designers: str = Field(description="Orders for Dept 3 & 4 (Audience & IA).")
    
    appendix: StrategyPaperAppendix

# --- SECTION 3: THE WRAPPERS (Required by Dispatcher) ---
class StrategyPatch(BaseModel):
    dept_id: str = Field(description="Registry ID: the_big_idea")
    version_note: str = Field(description="Brief history note.")
    content: StrategyPaperContent

class StrategySpatialOutput(BaseModel):
    thought_process: str = Field(description="Internal strategic planning.")
    user_message: str = Field(description="Proactive Partner message (Suggestion + Question).")
    suggested_project_name: Optional[str] = Field(default=None, description="2-3 word name suggested on Turn 2.")
    patch: Optional[StrategyPatch] = Field(default=None, description="The Brief update.")