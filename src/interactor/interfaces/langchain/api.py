""" Module provides a langchain API interface.
"""

from abc import ABC, abstractmethod
from typing import Any, List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import Runnable
from src.domain.entities.building.building import Building
from src.domain.entities.message.message import Message

class LangchainAPIInterface(ABC):
    """ LangchainAPIInterface class provides an interface for langchain API.
    """

    @abstractmethod
    def create_open_ai_llm(self) -> None:
        """ 
        Create OpenAI LLM and register it as dependency
        """
    
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
    def get_session_history(self, session_id) -> BaseChatMessageHistory:
        """ Get message history by session id

        :param session_id: session id
        :return: BaseChatMessageHistory
        """

    @abstractmethod
    def receive_prompt(self, sessionid: str, prompt: str) -> Message:
        """ 
        Receive prompt, receive the prompt from the client app
        :param sessionid: chat conversation session Id.
        :param prompt: chat message to be analyzed.
        """

    @abstractmethod
    def analyze_prompt(self, prompt: str, sessionId: str, filter_array: list, query: str) -> Message:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        :param filter_array: filters that needed for prompt analysis.
        :param query: formatted accurate query for the vector DB based on the user input.
        """

    @abstractmethod
    def feedback_prompt(self, prompt: str, sessionId: str, reask: bool, found: List[Building] | None) -> Message:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        :param reask: reask flag.
        """

    @abstractmethod
    def respond(self, template: Any, input_variables: list[str], runnable_input: dict[str, Any], session_id: str) -> Any | Runnable:
        """ 
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        """
    