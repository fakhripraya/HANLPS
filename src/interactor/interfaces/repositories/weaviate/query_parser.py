""" This module contains the interface for the QueryParser """

from abc import ABC, abstractmethod
from typing import Any

class QueryParserInterface(ABC):
    """ This class is the interface for the QueryParser
    """

    @abstractmethod
    def execute(self, dict: dict[str, Any]) -> str:
        """ Parse the incoming query.
        :return: output
        """
        