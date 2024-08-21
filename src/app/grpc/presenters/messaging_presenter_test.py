# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from src.interactor.dtos.messaging_dtos \
    import MessagingOutputDto
from domain.entities.message import Message
from .messaging_presenter import MessagingPresenter

def test_messaging_presenter(fixture_messaging_developer):
    message = Message(
        message_id=fixture_messaging_developer["message_id"],
        content=fixture_messaging_developer["content"],
    )
    output_dto = MessagingOutputDto(message)
    presenter = MessagingPresenter()
    assert presenter.present(output_dto) == {
        "message_id": fixture_messaging_developer["message_id"],
        "content": fixture_messaging_developer["content"],
    }
