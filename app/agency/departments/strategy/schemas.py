from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# STRICT ALLOWED TYPES for Journey
class JourneyNode(BaseModel):
    id: str
    type: Literal["input", "decision", "output", "default"] = Field(description="input=Start, decision=Branch, output=End, default=Action")
    label: str
    variant: Literal["hero", "sad", "default"] = Field(default="default", description="hero=Main Path, sad=Error Path")

class JourneyEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str = ""

class JourneyOutput(BaseModel):
    thought_process: str = Field(description="Explain the logic flow and player psychology.")
    nodes: List[JourneyNode]
    edges: List[JourneyEdge]