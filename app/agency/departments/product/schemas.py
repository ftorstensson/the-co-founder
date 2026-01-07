from pydantic import BaseModel, Field

class StrategyDocOutput(BaseModel):
    thought_process: str = Field(description="Internal reasoning and specialist debate.")
    user_message: str = Field(description="The friendly, human partner message shown in the chat bubble.")
    strategy_doc: str = Field(description="The professional STRATEGY.md markdown content for the canvas.")