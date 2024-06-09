import openai
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from src.interactor.interfaces.langchain.api import LangchainAPIInterface
from src.domain.constants import OPENAI, HUGGING_FACE

class LangchainAPI(LangchainAPIInterface):
    """ LangchainAPI class.
    """

    def __init__(self, llm_type, api_key) -> None: 
        llm 
        if llm_type == OPENAI:
            openai.api_key = api_key
            llm = openai
        elif llm_type == HUGGING_FACE:
            openai.api_key = api_key
            llm = openai

        self._llm_api = llm

    def analyze_prompt(self, chat_message) -> None:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """