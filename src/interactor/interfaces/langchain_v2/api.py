""" Module provides a langchain API v2 interface.
"""

from abc import ABC, abstractmethod
from langchain_core.runnables import Runnable
from src.domain.entities.building.building import Building
from src.domain.entities.message.message import Message
from typing import Any


class LangchainAPIV2Interface(ABC):
    """LangchainAPIV2Interface class provides an interface for langchain API v2."""

    @abstractmethod
    def clear_messaging_history(self, session_id) -> bool:
        """
        Clear message history
        :param session_id: chat session id.
        :return: bool
        """

    @abstractmethod
    def execute_search_agent(self, session_id: str, prompt: str) -> Message:
        """
        Execute search agent boarding house search
        :param session_id: chat session id.
        :param prompt: the search prompt.
        :return: Message
        """
