""" This module contains the interface for the PromptParser """

from abc import ABC, abstractmethod

class PromptParserInterface(ABC):
    """ This class is the interface for the PromptParser
    """

    @abstractmethod
    def execute(self, input: str) -> str:
        """ Parse the incoming prompt.
        :param prompt: Prompt to be parse.
        :return: output
        """
        