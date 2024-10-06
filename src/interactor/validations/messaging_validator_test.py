# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import pytest
from interactor.validations.messaging_validator import MessagingInputDtoValidator
from src.interactor.errors.error_classes import FieldValueNotPermittedException


def test_messaging_validator_valid_data(mocker, fixture_messaging_developer):
    mocker.patch(
        "src.interactor.validations.base_input_validator.\
BaseInputValidator.verify"
    )
    input_data = {
        "content": fixture_messaging_developer["content"],
    }
    schema = {
        "content": {"type": "string", "required": True, "empty": False},
    }
    validator = MessagingInputDtoValidator(input_data)
    validator.validate()
    validator.verify.assert_called_once_with(schema)  # pylint: disable=E1101


def test_messaging_validator_empty_input(fixture_messaging_developer):
    # We are doing just a simple test as the complete test is done in
    # base_input_validator_test.py
    input_data = {
        "content": fixture_messaging_developer["content"],
    }
    validator = MessagingInputDtoValidator(input_data)
    with pytest.raises(ValueError) as exception_info:
        validator.validate()
    assert str(exception_info.value) == "Content: empty values not allowed"


def test_messaging_custom_validation():
    input_data = {
        "content": "This Message Failed",
    }
    validator = MessagingInputDtoValidator(input_data)
    with pytest.raises(FieldValueNotPermittedException) as exception_info:
        validator.validate()
    assert str(exception_info.value) == "Content: This Message Failed is not permitted"
