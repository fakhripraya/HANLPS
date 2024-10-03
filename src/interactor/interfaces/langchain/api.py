""" Module provides a langchain API interface.
"""

from abc import ABC, abstractmethod
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import Runnable
from src.domain.entities.building.building import Building
from src.domain.entities.message.message import Message
from typing import Any

class LangchainAPIInterface(ABC):
    """ LangchainAPIInterface class provides an interface for langchain API.
    """

    @abstractmethod
    def create_open_ai_llm(self) -> None:
        """ 
        Create OpenAI LLM and register it as dependency
        """
    
    @abstractmethod
    def create_gemini_llm(self) -> None:
        """ 
        Create Gemini LLM and register it as dependency
        """
    
    @abstractmethod
    def create_huggingface_llm(self) -> None:
        """ 
        Create Huggingface LLM and register it as dependency
        """
        
    @abstractmethod
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
         """ Get message history by session id
        :param session_id: chat session id
        :return: BaseChatMessageHistory
        """

    @abstractmethod
    def analyze_prompt(self, session_id: str, prompt: str) -> Message:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param session_id: chat session id.
        :param prompt: chat message to be analyzed.
        """

    @abstractmethod
    def vector_db_retrieval(self, prompt: str, session_id: str, filter_array: dict[str, list], query: str) -> Message:
        """
        Vector database data retrieval process
        :param prompt: chat message to be analyzed.
        :param session_id: session id of the chat.
        :param filter_array: filters that needed for prompt analysis.
        :param query: query for vector data retrieval with weaviate.
        """

    @abstractmethod
    def feedback_prompt(self, prompt: str, session_id: str, reask: bool, found: list[Building] | None) -> Message:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        :param session_id: session id of the chat.
        :param reask: reask flag.
        :param found: data found elements.
        """

    @abstractmethod
    def respond(self, template: Any, input_variables: list[str], runnable_input: dict[str, Any], session_id: str) -> Any | Runnable:
        """ 
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        """
    