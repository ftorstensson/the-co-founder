from pydantic import BaseModel, Field
from typing import List, Optional, ForwardRef

# Define Recursive Model Reference
WireframeNode = ForwardRef('WireframeNode')

class LayoutProps(BaseModel):
    # ALL FIELDS OPTIONAL with Defaults
    mode: str = Field(default="stack", description="Layout mode: 'stack', 'dock', 'none'")
    direction: str = Field(default="vertical", description="'vertical' or 'horizontal'")
    gap: int = Field(default=16)
    padding: int = Field(default=16)
    dock_edge: str = Field(default="none", description="Edge: 'top', 'bottom', 'left', 'right', 'none'")
    align: str = Field(default="stretch", description="'start', 'center', 'end', 'stretch'")

class WireframeNode(BaseModel):
    # Auto-fill ID if missing (handled by Pydantic default_factory if we wanted, 
    # but the AI is usually good at IDs. If not, the frontend can handle a missing ID gracefully-ish).
    # Ideally, we keep ID required, but let's make it default to "unknown" to prevent crash.
    id: str = Field(default="generated-id", description="Unique identifier")
    
    # Relaxed Type: String allows "Button" or "PrimaryButton" without crashing
    type: str = Field(default="Container", description="Component type")
    
    label: str = Field(default="Element", description="Text content")
    
    # PERMISSIVE DEFAULTS
    layout: LayoutProps = Field(default_factory=LayoutProps)
    children: List[WireframeNode] = Field(default_factory=list)

# Resolve Recursion
WireframeNode.update_forward_refs()

class WireframeOutput(BaseModel):
    thought_process: str = Field(description="Reasoning about layout.", default="Generated Layout")
    root: WireframeNode = Field(description="The root MobileScreen node.")