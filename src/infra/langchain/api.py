import openai
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from src.interactor.interfaces.langchain.api import LangchainAPIInterface
from src.domain.constants import OPENAI, HUGGING_FACE

class LangchainAPI(LangchainAPIInterface):
    """ LangchainAPI class.
    """

    def __init__(self, llm_type, api_key) -> None: 
        client 
        if llm_type == OPENAI:
            openai.api_key = api_key
            client = openai
        elif llm_type == HUGGING_FACE:
            openai.api_key = api_key
            client = openai

        self._client = client

    def receive_prompt(self, prompt) -> None:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """

    def analyze_prompt(self, prompt) -> None:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """

    def feedback_prompt(self, prompt) -> None:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param chat_message: chat message to be analyzed.
        """

    def respond(self, messages, client) -> None:
        """ 
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param chat_message: chat message to be analyzed.
        """
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=1,
        )
        return response.choices[0].message.content