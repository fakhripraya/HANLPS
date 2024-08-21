""" Module for MessagingInMemoryRepository
"""

from src.domain.entities.message.message import Message
from src.interactor.interfaces.repositories.in_memory.messaging_repository \
    import MessagingRepositoryInterface

class MessagingInMemoryRepository(MessagingRepositoryInterface):
    """ Repository for Messaging
    """

    def create(
        self,
        input,
        output,
        output_content = None
    ) -> Message:
        message = Message(
            input=input,
            output=output,
            output_content=output_content,
        )
        return message
