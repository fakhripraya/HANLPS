""" This module contains the interface for the MessagingRepository
"""

from abc import ABC, abstractmethod
from typing import Optional
from src.domain.value_objects import MessageId
from src.domain.entities.message import Message

class MessagingRepositoryInterface(ABC):
    """ This class is the interface for the MessagingRepository
    """

    @abstractmethod
    def get(self, message_id: MessageId) -> Optional[Message]:
        """ Get a Message by id

        :param profession_id: MessageId
        :return: Message
        """

    @abstractmethod
    def create(self, content: str) -> Optional[Message]:
        """ Create a Message

        :param content: Message content
        :return: MessageId
        """

    @abstractmethod
    def update(self, message: Message) -> Optional[Message]:
        """ Update a Message

        :param Profession: Message
        :return: Message
        """
