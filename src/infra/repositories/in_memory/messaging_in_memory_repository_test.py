# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from .messaging_in_memory_repository import MessagingInMemoryRepository


def test_messaging_in_memory_repository(fixture_messaging_developer):
    repository = MessagingInMemoryRepository()
    assert repository.create(
        fixture_messaging_developer["content"],
    )
