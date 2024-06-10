""" Module provides a langchain API interface.
"""

from abc import ABC, abstractmethod

class LangchainAPIInterface(ABC):
    """ LangchainAPIInterface class provides an interface for langchain API.
    """

    @abstractmethod
    def receive_prompt(self, prompt:str) -> None:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """

    @abstractmethod
    def analyze_prompt(self, prompt:str) -> None:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """

    @abstractmethod
    def feedback_prompt(self, prompt:str) -> None:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param chat_message: chat message to be analyzed.
        """

    @abstractmethod
    def respond(self, messages:str) -> None:
        """ 
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """
    