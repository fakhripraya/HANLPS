""" Module for the MessagingPresenterInterface
"""

from typing import Dict
from abc import ABC, abstractmethod
from src.interactor.dtos.messaging_dtos \
    import MessagingOutputDto

class MessagingPresenterInterface(ABC):
    """ Class for the Interface of the MessagingPresenter
    """
    @abstractmethod
    def present(self, output_dto: MessagingOutputDto) -> Dict:
        """ Present the Profession
        """
