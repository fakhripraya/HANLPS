""" Module for the MessagingPresenter
"""

from src.interactor.dtos.messaging_dtos import MessagingOutputDto
from src.interactor.interfaces.presenters.message_presenter import (
    MessagingPresenterInterface,
)


class MessagingPresenter(MessagingPresenterInterface):
    """Class for the MessagingPresenter"""

    def present(self, output_dto: MessagingOutputDto) -> dict:
        """Present the Message in dictionary
        :param output_dto: MessagingOutputDto
        :return: Dict
        """
        return {
            "input": output_dto.input,
            "output": output_dto.output,
            "output_content": output_dto.output_content,
        }
