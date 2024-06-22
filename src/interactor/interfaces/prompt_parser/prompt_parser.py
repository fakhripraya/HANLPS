""" This module contains the interface for the PromptParser """

from abc import ABC, abstractmethod
from pyparsing import Any

class PromptParserInterface(ABC):
    """ This class is the interface for the PromptParser
    """

    @abstractmethod
    def execute(self, input: str, templates: dict[list[str], Any]) -> bool:
        """ Parse the incoming prompt.
        :param prompt: Prompt to be parse.
        :return: output
        """
        