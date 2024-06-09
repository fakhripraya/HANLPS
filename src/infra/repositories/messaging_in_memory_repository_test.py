# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from src.domain.entities.message import Message
from .messaging_in_memory_repository import MessagingInMemoryRepository

def test_messaging_in_memory_repository(fixture_messaging_developer):
    repository = MessagingInMemoryRepository()
    message = repository.create(
        fixture_messaging_developer["content"],
    )
    response = repository.get(message.message_id)
    assert response.content == fixture_messaging_developer["content"]
    new_message = Message(
        message.message_id,
        "new content",
    )
    response_update = repository.update(new_message)
    assert response_update.content == "new content"
