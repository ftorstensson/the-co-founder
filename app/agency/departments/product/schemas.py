from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# --- LEVEL 3: PROJECT MEMORY ---
class DecisionEntry(BaseModel):
    id: str = Field(description="e.g. DEC-001")
    statement: str = Field(description="The atomic decision or vision anchor.")
    state: Literal["provisional", "locked", "deprecated"] = Field(default="provisional")
    rationale: str = Field(description="The E.L.I. reasoning behind this decision.")
    layer: str = Field(default="STRATEGY", description="Which layer this decision anchors.")

# --- SECTION 1: THE APPENDIX (Architectural Reasoning) ---
class StrategyPaperAppendix(BaseModel):
    architect_logic_a: str = Field(description="Primary Specialist logic. MANDATE: 4+ paragraphs of dense Markdown analysis. Use E.L.I. protocol. Do not summarize the Director; introduce new strategic leverage.")
    architect_logic_b: str = Field(description="Secondary Specialist logic. MANDATE: 4+ paragraphs of dense Markdown analysis. Focus on moats, psychological triggers, or economic logic.")
    architect_logic_c: str = Field(description="Tertiary Specialist logic. MANDATE: 4+ paragraphs of dense Markdown analysis. Focus on technical strategic sacrifices and the 95/5 build rule.")
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

class MissionManifesto(BaseModel):
    problem_statement: str = Field(default="", description="The core project intent.")
    desired_outcome: str = Field(default="", description="The successful future state.")
    magic_differentiator: str = Field(default="", description="The 5 percent magic/soul.")
    target_user: str = Field(default="", description="Primary audience.")
    verbatim_quotes: List[str] = Field(default_factory=list, description="Sacred user language.")
    emotional_drivers: List[str] = Field(default_factory=list, description="What animates the Director.")
    unresolved_tensions: List[str] = Field(default_factory=list, description="Conflicts to resolve.")

class ScribeOutput(BaseModel):
    mission_manifesto: MissionManifesto = Field(description="The updated project state.")
    suggested_project_name: Optional[str] = Field(default=None)
    hiring_authorized: bool = Field(default=False)
    new_decisions: List[DecisionEntry] = Field(default_factory=list)

class StrategySpatialOutput(BaseModel):
    thought_process: str = Field(description="Internal partner reasoning.")
    user_message: str = Field(description="The social response to the Director.")