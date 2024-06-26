""" Module provides a langchain API interface.
"""

from abc import ABC, abstractmethod
from langchain_core.chat_history import BaseChatMessageHistory

class LangchainAPIInterface(ABC):
    """ LangchainAPIInterface class provides an interface for langchain API.
    """

    @abstractmethod
    def create_open_ai_llm(self, api_key: str) -> None:
        """ 
        Create OpenAI LLM and register it as dependency
        """
    
    def create_gemini_llm(self) -> None:
        """ 
        Create Gemini LLM and register it as dependency
        """
    
    @abstractmethod
    def create_huggingface_llm(self, api_key: str) -> None:
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
    def receive_prompt(self, prompt:str) -> str:
        """ 
        Receive prompt, receive the prompt from the client app
        :param prompt: chat message to be analyzed.
        """

    @abstractmethod
    def analyze_prompt(self, prompt:str, filter_array:list) -> str:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        :param filter_array: filters that needed for prompt analysis.
        """

    @abstractmethod
    def feedback_prompt(self, prompt:str, reask:bool) -> str:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        :param reask: reask flag.
        """

    @abstractmethod
    def respond(self, prompt:str) -> str:
        """ 
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        """
    