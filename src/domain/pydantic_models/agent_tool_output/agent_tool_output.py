import json
from typing import Any

from pydantic import BaseModel, Field, model_validator
from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter


class AgentToolOutput(BaseModel):
    input_code: str | None = Field(
        description="The tool code, used to identify which tool is used"
    )
    input_field: BuildingsFilter | None = Field(
        description="The formatted input field, used for building filter"
    )
    @model_validator(mode="before")
    def parse_raw_input(cls, values: Any) -> Any:
        """
        Custom validator to handle and parse raw JSON strings into a structured format.
        """
        if isinstance(values, str):  # If raw JSON input is provided as a string
            try:
                result = values.strip("`").strip("json").strip("`").strip()
                data_dict = json.loads(result)
                return data_dict
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")
        elif isinstance(values, dict):  # Already a dict, just return as is
            return values
        return values  # Return as is if unrecognized