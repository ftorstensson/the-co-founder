from pydantic import BaseModel, Field
from typing import List, Optional

# --- SECTION 1: THE APPENDIX (Architectural Reasoning) ---
class StrategyPaperAppendix(BaseModel):
    architect_logic_a: str = Field(description="Visionary logic. MANDATE: 4+ paragraphs of Markdown. Bring NEW ideas.")
    architect_logic_b: str = Field(description="Commercial logic. MANDATE: 4+ paragraphs of Markdown. Focus on Moats.")
    architect_logic_c: str = Field(description="Build logic. MANDATE: 4+ paragraphs of Markdown. Focus on Sacrifice.")
    adversarial_tension: str = Field(description="Detailed teardown of disagreements.")

# --- SECTION 2: THE VENTURE BRIEF CONTENT ---
class StrategyPaperContent(BaseModel):
    masthead: str = Field(description="LABEL: e.g. THE BIG IDEA")
    headline: str = Field(description="A provocative, short title.")
    
    # Paper 1: The Big Idea
    one_sentence_idea: Optional[str] = Field(None)
    core_problem: Optional[str] = Field(None)
    money_logic: Optional[str] = Field(None)
    critical_assumptions: Optional[str] = Field(None)
    
    # Paper 2: Market Research
    market_shape: Optional[str] = Field(None)
    distribution_wedge: Optional[str] = Field(None)
    competition: Optional[str] = Field(None)
    market_gaps: Optional[str] = Field(None)
    how_we_win: Optional[str] = Field(None)

    # Paper 3: Audience Mapping
    audience_hierarchy: Optional[str] = Field(None)
    hiring_conditions: Optional[str] = Field(None)
    influence_dynamics: Optional[str] = Field(None)
    audience_profiles: Optional[str] = Field(None)
    success_moments: Optional[str] = Field(None)

    # Paper 4: User Experience
    convention_baseline: Optional[str] = Field(None)
    magic_layer: Optional[str] = Field(None)
    initial_hook: Optional[str] = Field(None)
    habit_loop: Optional[str] = Field(None)

    # Paper 5: The MVP
    must_haves: Optional[str] = Field(None)
    main_objects: Optional[str] = Field(None)
    deferred_features: Optional[str] = Field(None)
    build_readiness: Optional[str] = Field(None)

    appendix: StrategyPaperAppendix

# --- SECTION 3: THE WRAPPERS ---
class StrategyPatch(BaseModel):
    dept_id: str = Field(description="the_big_idea, market_research, etc.")
    version_note: str = Field(description="Brief history note.")
    content: StrategyPaperContent

class StrategySpatialOutput(BaseModel):
    thought_process: str = Field(description="Internal reasoning.")
    user_message: str = Field(description="The Partner's response.")
    suggested_project_name: Optional[str] = Field(default=None)
    hiring_authorized: bool = Field(default=False)
    target_dept_id: str = Field(default="the_big_idea")