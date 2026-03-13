# [FUNCTIONAL LEDGER - DO NOT REMOVE]
# 1. [MISSION_MANIFESTO]: Explicit buckets. problem_statement is the Official Brief.
# 2. [SCRIBE_OUTPUT]: user_confirmed_start for sentiment detection.
# 3. [STRATEGY_PAPERS]: BigIdea, Opportunity, People, Experience, MVP.
# 4. [JOURNEY_LOGIC]: JourneyNode, JourneyEdge, JourneyOutput.

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Dict

class StrategyPaperAppendix(BaseModel):
    architect_logic_a: str = Field(description='Full ELI analysis from Specialist 1')
    architect_logic_b: str = Field(description='Full ELI analysis from Specialist 2')
    architect_logic_c: str = Field(description='Full ELI analysis from Specialist 3')
    adversarial_tension: str = Field(description='The friction point between the specialists')

class BigIdeaContent(BaseModel):
    masthead: str = 'THE BIG IDEA'
    headline: str
    insight: str
    one_sentence: str
    problem: str
    money: str
    must_be_true: str
    anti_vision: str
    appendix: StrategyPaperAppendix

class OpportunityContent(BigIdeaContent): masthead: str = 'THE OPPORTUNITY'
class PeopleContent(BigIdeaContent): masthead: str = 'THE PEOPLE'
class ExperienceContent(BigIdeaContent): masthead: str = 'THE EXPERIENCE'
class MVPContent(BigIdeaContent): masthead: str = 'THE MVP'

class MissionManifesto(BaseModel):
    core_idea: str = ''
    target_user: str = ''
    founder_frustration: str = ''
    competitor_belief: str = ''
    business_model: str = ''
    success_sentence: str = ''
    problem_statement: str = '' # THE OFFICIAL BRIEF (UI + SPECIALISTS)
    verbatim_quotes: List[str] = []
    emotional_drivers: List[str] = []
    unresolved_tensions: List[str] = []

class ScribeOutput(BaseModel):
    mission_manifesto: MissionManifesto
    user_confirmed_start: bool = Field(default=False)
    missing_checklist_items: List[str] = []
    whisper: Optional[str] = None # Tactical note for the PM HUD 
    suggested_project_name: Optional[str] = None
    hiring_authorized: bool = False

class StrategyPatch(BaseModel):
    dept_id: str
    version_note: str
    content: Any

class StrategySpatialOutput(BaseModel):
    thought_process: str
    user_message: str
    suggested_project_name: Optional[str] = None
    manifesto: Optional[MissionManifesto] = None

class JourneyNode(BaseModel):
    id: str
    type: Literal["input", "decision", "output", "default"]
    label: str
    variant: Literal["hero", "sad", "default"] = "default"

class JourneyEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str = ""

class JourneyOutput(BaseModel):
    thought_process: str
    nodes: List[JourneyNode]
    edges: List[JourneyEdge]
