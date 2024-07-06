""" This module contains the interface for the MessagingRepository
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.message.message import Message

class MessagingRepositoryInterface(ABC):
    """ This class is the interface for the MessagingRepository
    """

    @abstractmethod
    def create(
        self,
        input: str,
        output: str,
        output_content: List[str] | None,
    ) -> Optional[Message]:
        """ Create a Message

        :param input: Input message
        :param output: Output message
        :param output_content: Output message content
        :return: MessageId
        """
