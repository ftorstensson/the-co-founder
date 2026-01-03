from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# STRICT ALLOWED TYPES for Sitemap
class SitemapNode(BaseModel):
    id: str
    type: Literal["page", "purpose"] = Field(description="page=Screen, purpose=Annotation Dot")
    label: str
    # Rich Data (Required for Sitemap)
    template: str = Field(description="e.g. 'Feed', 'Dashboard', 'Modal'")
    content: List[str] = Field(description="Top 3-5 content blocks on this page")
    goal: str = Field(description="Primary user goal for this page")

class SitemapEdge(BaseModel):
    id: str
    source: str
    target: str

class SitemapOutput(BaseModel):
    thought_process: str = Field(description="Explain the hierarchy and content strategy.")
    nodes: List[SitemapNode]
    edges: List[SitemapEdge]