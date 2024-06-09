# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from .messaging_dtos import MessagingInputDto

def test_messaging_dto_valid(fixture_messaging_developer):
    input_dto = MessagingInputDto(
        content=fixture_messaging_developer["content"],
    )
    assert input_dto.content == fixture_messaging_developer["content"]
    assert input_dto.to_dict() == {
        "content": fixture_messaging_developer["content"],
    }
