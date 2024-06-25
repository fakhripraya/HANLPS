""" Module for LangchainAPI
"""

from src.interactor.interfaces.langchain.api import LangchainAPIInterface
from src.infra.langchain.prompt_parser.prompt_parser import PromptParser
from src.infra.weaviate.api import WeaviateAPI
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.domain.constants import OPENAI, HUGGING_FACE, GEMINI
from configs.config import ADVERTISING_PIC_NUMBER, SERVICE_PIC_NUMBER, \
    OPENAI_MODEL, HUGGINGFACE_MODEL, GEMINI_MODEL, GEMINI_API_KEY, USE_MODULE
from src.domain.prompt_templates import chat_template, analyzer_template
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline
from langchain_google_genai import ChatGoogleGenerativeAI
from src.domain.constants import BUILDINGS_COLLECTION_NAME
from weaviate.classes.query import MetadataQuery
from weaviate.classes.query import Filter

class LangchainAPI(LangchainAPIInterface, WeaviateAPI):
    """ LangchainAPI class.
    """

    def __init__(self, llm_type: str, api_key: str, logger: LoggerInterface) -> None: 
        self._api_key = api_key
        self._logger = logger
        self._store = {}
        
        if llm_type == OPENAI:
            self.create_open_ai_llm()
        elif llm_type == HUGGING_FACE:
            self.create_huggingface_llm()
        elif llm_type == GEMINI:
            self.create_gemini_llm()
        else:
            raise Exception("No LLM Found")
        
        self._prompt_parser = PromptParser(self._client)
        self._templates = {
            "analyzer_template": [analyzer_template],
            "chat_template": chat_template
        }

    def create_open_ai_llm(self) -> None:
        """ 
        Create OpenAI LLM and register it as dependency
        """
        client = ChatOpenAI(model=OPENAI_MODEL, api_key=self._api_key)
        self._client = client
        WeaviateAPI.__init__(self, OPENAI if int(USE_MODULE) == 1 else None, self._logger)
        
    def create_gemini_llm(self) -> None:
        """ 
        Create Gemini LLM and register it as dependency
        """
        baseUrl = 'https://generativelanguage.googleapis.com'
        version = 'v1beta'
        client = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0,
            baseUrl=baseUrl,
            max_retries=0,
            version=version
        )
        self._client = client
        WeaviateAPI.__init__(self, GEMINI if int(USE_MODULE) == 1 else None, self._logger)
        
    def create_huggingface_llm(self) -> None:
        """ 
        Create Huggingface LLM and register it as dependency
        """
        # NOTE 
        # doesn't support Bahasa Indonesia 
        client = HuggingFacePipeline.from_model_id(
            model_id=HUGGINGFACE_MODEL,
            task="text-generation",
            pipeline_kwargs={
                "max_new_tokens": 100,
                "top_k": 50,
                "temperature": 0.1,
            },
        )
        self._client = client
        WeaviateAPI.__init__(self, HUGGING_FACE if int(USE_MODULE) == 1 else None, self._logger)

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
        
        if bool(result) is True:
            buildings_collection = self._weaviate_client.collections.get(BUILDINGS_COLLECTION_NAME)
            response = buildings_collection.query.hybrid(
                query="kosan yang kamar mandi dalam dan parkiran motor harga 1.5 min",
                target_vector="property_description",
                filters=(
                    Filter.all_of([
                        Filter.by_property("housing_price").greater_than(300),
                        Filter.by_property("housing_price").less_than(700),
                        Filter.by_property("housing_price").equal(700),
                    ])
                ),
                limit=2,
                return_metadata=MetadataQuery(distance=True,certainty=True)
            )

            for o in response.objects:
                print(o.properties)
                print(o.metadata.distance)
                print(o.metadata.certainty)
        
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
        result = with_message_history.invoke(
            {
                "input": prompt,
                "service_pic_number": SERVICE_PIC_NUMBER,
                "advertising_pic_number": ADVERTISING_PIC_NUMBER
            },
            config={"configurable": {"session_id": "abc123"}}
        )
        output = self.respond(result)
        
        return output

    def respond(self, prompt) -> str:
        """ 
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        """
        return prompt