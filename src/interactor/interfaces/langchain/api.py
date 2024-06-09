""" Module provides a langchain API interface.
"""

from abc import ABC, abstractmethod

class LangchainAPIInterface(ABC):
    """ LangchainAPIInterface class provides an interface for langchain API.
    """

    @abstractmethod
    def analyze_prompt(self, chat_message:str) -> None:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """
        
    