""" Module provides a langchain API interface.
"""

from abc import ABC, abstractmethod

class LangchainAPIInterface(ABC):
    """ LangchainAPIInterface class provides an interface for langchain API.
    """

    @abstractmethod
    def create_open_ai_llm(self, api_key: str) -> None:
        """ 
        Create OpenAI LLM and register it as dependency
        :param api_key: the OpenAi api key
        """
    
    @abstractmethod
    def create_huggingface_llm(self, api_key: str) -> None:
        """ 
        Create Huggingface LLM and register it as dependency
        :param api_key: the Huggingface api key
        """

    @abstractmethod
    def receive_prompt(self, prompt:str) -> str:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """

    @abstractmethod
    def analyze_prompt(self, prompt:str) -> str:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """

    @abstractmethod
    def feedback_prompt(self, prompt:str) -> str:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param chat_message: chat message to be analyzed.
        """

    @abstractmethod
    def respond(self, prompt:str) -> str:
        """ 
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """
    