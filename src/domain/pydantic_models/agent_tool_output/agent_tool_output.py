import json
from typing import Any

from pydantic import BaseModel, Field, model_validator
from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter


class AgentToolOutput(BaseModel):
    input_code: str | None = Field(
        default=None,
        description="The tool code, used to identify which tool is used"
    )
    input_field: BuildingsFilter | None = Field(
        default=None,
        description="The formatted input field, used for building filter"
    )
    chat_output: str | None = Field(
        default=None,
        description="Chat output produced by the agent"
    )

    @model_validator(mode="before")
    def parse_raw_input(cls, values: Any) -> Any:
        """
        Custom validator to handle and parse raw JSON strings into a structured format.
        """
        if isinstance(values, str):
            try:
                data_dict = json.loads(values)
                return data_dict
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")
        
        return values