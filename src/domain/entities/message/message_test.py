# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from .message import Message


def test_message_creation(fixture_message_developer):
    message = Message(
        message_id=fixture_message_developer["message_id"],
        content=fixture_message_developer["content"],
    )
    assert message.content == fixture_message_developer["content"]


def test_message_from_dict(fixture_message_developer):
    message = Message.from_dict(fixture_message_developer)
    assert message.content == fixture_message_developer["content"]


def test_message_to_dict(fixture_message_developer):
    message = Message.from_dict(fixture_message_developer)
    assert message.to_dict() == fixture_message_developer


def test_message_comparison(fixture_message_developer):
    message_1 = Message.from_dict(fixture_message_developer)
    message_2 = Message.from_dict(fixture_message_developer)
    assert message_1 == message_2
