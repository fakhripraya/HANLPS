from pydantic import BaseModel, Field
from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter

class UserPrompt(BaseModel):
    action_code: str | None = Field(
        description="The action code for system task, if applicable"
    )
    input_field: BuildingsFilter | None = Field(
        description="The input field for system task, If applicable."
    )
    chat_output: str | None = Field(
        description="The chat output from the AI agent, If applicable."
    )