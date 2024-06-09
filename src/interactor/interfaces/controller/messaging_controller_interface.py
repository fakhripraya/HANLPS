""" This module contains the MessagingControllerInterface class
"""

from typing import Dict
from abc import ABC, abstractmethod

class MessagingControllerInterface(ABC):
    """ This class is the interface for the Messaging Controller class
    """

    def get_message(self, json_input) -> None:
        """ Get Message packet from the GRPC Client
        :param json_input: Input data
        :raises: ValueError if message content are missing.
        """

    @abstractmethod
    def execute(self) -> Dict:
        """ Executes the controller
        :returns: Message processed and send responses
        """
