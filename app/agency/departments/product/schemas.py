from pydantic import BaseModel, Field

class StrategyDocOutput(BaseModel):
    thought_process: str = Field(description="The internal debate and reasoning behind the strategy.")
    content: str = Field(description="The final Strategy Document in Markdown format.")