""" Module provides a langchain API interface.
"""

from abc import ABC, abstractmethod
from langchain_core.runnables import Runnable
from src.domain.entities.building.building import Building
from src.domain.entities.message.message import Message
from src.domain.entities.action.action import Action
from typing import Any


class LangchainAPIInterface(ABC):
    """LangchainAPIInterface class provides an interface for langchain API."""

    @abstractmethod
    def analyze_prompt(self, session_id: str, prompt: str) -> tuple[Action, Message]:
        """
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param session_id: chat session id.
        :param prompt: chat message to be analyzed.
        """

    @abstractmethod
    def vector_db_retrieval(
        self,
        prompt: str,
        session_id: str,
        filter_array: dict[str, list],
        facility_query: str,
        location_query: str,
    ) -> Message:
        """
        Vector database data retrieval process
        :param prompt: chat message to be analyzed.
        :param session_id: session id of the chat.
        :param filter_array: filters that needed for prompt analysis.
        :param facility_query: query by facility to retrieve vector data from weaviate.
        :param location_query: query by location to retrieve vector data from weaviate.
        """

    @abstractmethod
    def feedback_prompt(
        self, prompt: str, session_id: str, reask: bool, found: list[Building] | None
    ) -> Message:
        """
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        :param session_id: session id of the chat.
        :param reask: reask flag.
        :param found: data found elements.
        """

    @abstractmethod
    def respond(
        self,
        template: Any,
        input_variables: list[str],
        runnable_input: dict[str, Any],
        session_id: str,
    ) -> Any | Runnable:
        """
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        """
