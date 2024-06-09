# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Dict
import pytest
from src.interactor.validations.base_input_validator import BaseInputValidator

class BaseValidator(BaseInputValidator):
    def __init__(self, data: Dict):
        super().__init__(data)
        self.schema = {
                "content": {
                    "type": "string",
                    "required": True,
                    "empty": False
                },
        }

    def validate(self):
        super().verify(self.schema)

def test_base_validator_with_valid_data():
    data = {'content': 'test'}
    validator = BaseValidator(data)
    validator.validate()

def test_base_validator_with_empty_data():
    data = {'content': ''}
    validator = BaseValidator(data)
    with pytest.raises(ValueError) as exception_info:
        validator.validate()
    assert str(exception_info.value) == "Content: empty values not allowed"

def test_base_validator_without_required_data():
    data = {}
    validator = BaseValidator(data)
    with pytest.raises(ValueError) as exception_info:
        validator.validate()
    assert str(exception_info.value) == "Content: required field"
