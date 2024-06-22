""" Module for LangchainAPI
"""

from src.interactor.interfaces.langchain.api import LangchainAPIInterface
from src.infra.langchain.prompt_parser.prompt_parser import PromptParser
from src.infra.weaviate.api import WeaviateAPI
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.domain.constants import OPENAI, HUGGING_FACE
from src.domain.prompt_templates import chat_template, analyzer_template
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
    
class LangchainAPI(LangchainAPIInterface, WeaviateAPI):
    """ LangchainAPI class.
    """

    def __init__(self, llm_type: str, api_key: str, logger: LoggerInterface) -> None: 
        # TODO: Implement weaviate here
        self._api_key = api_key
        self._logger = logger
        self._store = {}
        
        if llm_type == OPENAI:
            self.create_open_ai_llm()
        elif llm_type == HUGGING_FACE:
            self.create_huggingface_llm()

    def create_open_ai_llm(self) -> None:
        """ 
        Create OpenAI LLM and register it as dependency
        """
        client = ChatOpenAI(model="gpt-4", api_key=self._api_key)
        WeaviateAPI.__init__(self, self._logger)
        
        self._client = client
        self._prompt_parser = PromptParser(self._client)
        self._templates = {
            "analyzer_template": [analyzer_template],
            "chat_template": chat_template
        }
        
        # with_message_history = RunnableWithMessageHistory(
        #     runnable,
        #     self.get_session_history,
        #     input_messages_key="input",
        #     history_messages_key="history",
        # )

    def create_huggingface_llm(self) -> None:
        """ 
        Create Huggingface LLM and register it as dependency
        """

    def get_session_history(self, session_id) -> BaseChatMessageHistory:
        """ Get message history by session id

        :param session_id: session id
        :return: BaseChatMessageHistory
        """
        if session_id not in self._store:
            self._store[session_id] = ChatMessageHistory()
        return self._store[session_id]

    def receive_prompt(self, prompt) -> str:
        """ 
        Receive prompt, receive the prompt from the client app
        :param prompt: chat message to be analyzed.
        """
        output = self.analyze_prompt(prompt)
        return output

    def analyze_prompt(self, prompt) -> str:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        """
        result = self._prompt_parser.execute(prompt, self._templates)
        print(result)
        output = self.feedback_prompt(prompt)
        
        return output

    def feedback_prompt(self, prompt) -> str:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        """
        template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self._templates["chat_template"],
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )
        chain = template | self._client | StrOutputParser()
        with_message_history = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        result = with_message_history.invoke({"input": prompt})
        output = self.respond(result)
        
        return output

    def respond(self, prompt) -> str:
        """ 
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        """
        # messages = [{"role": "user", "content": prompt}]
        # response = self._client.chat.completions.create(
        #     model="gpt-4",
        #     messages=messages,
        #     temperature=0.1,
        # )
        # return response.choices[0].message.content
        return prompt