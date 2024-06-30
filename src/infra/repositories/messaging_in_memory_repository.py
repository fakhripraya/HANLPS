""" Module for MessagingInMemoryRepository
"""

from typing import Dict
import copy
import uuid
from src.domain.entities.message.message import Message
from src.interactor.interfaces.repositories.messaging_repository \
    import MessagingRepositoryInterface
from src.domain.value_objects import MessageId

class MessagingInMemoryRepository(MessagingRepositoryInterface):
    """ InMemory Repository for Messaging
    """
    def __init__(self) -> None:
        self._data: Dict[MessageId, Message] = {}

    def get(self, message_id: MessageId) -> Message:
        """ Get Message by id

        :param message_id: MessageId
        :return: Message
        """
        return copy.deepcopy(self._data[message_id])

    def create(self, content: str) -> Message:
        message = Message(
            message_id=uuid.uuid4(),
            content=content,
        )
        self._data[message.message_id] = copy.deepcopy(message)
        return copy.deepcopy(self._data[message.message_id])

    def update(self, message: Message) -> Message:
        self._data[message.message_id] = copy.deepcopy(message)
        return copy.deepcopy(self._data[message.message_id])
