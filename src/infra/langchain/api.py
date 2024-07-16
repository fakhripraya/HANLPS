""" Module for LangchainAPI
"""

# Standard and third-party libraries
import ast
import json
from typing import List

# Source-specific imports
from configs.config import (
    ADVERTISING_PIC_NUMBER, SERVICE_PIC_NUMBER,
    OPENAI_MODEL, HUGGINGFACE_MODEL, GEMINI_MODEL,
    GEMINI_API_KEY, USE_MODULE
)
from src.domain.entities.message.message import Message
from src.domain.constants import OPENAI, HUGGING_FACE, GEMINI, BUILDINGS_COLLECTION_NAME
from src.domain.prompt_templates import (
    chat_template,
    analyzer_template,
    filter_analyzer_template,
    reask_template,
    building_found_template
)
from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter
from src.infra.langchain.prompt_parser.prompt_parser import PromptParser
from src.infra.weaviate.api import WeaviateAPI
from src.interactor.interfaces.langchain.api import LangchainAPIInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.weaviate.schema.collections.buildings.buildings import append_housing_price_filters
from src.domain.entities.building.building import Building

# Langchain and related libraries
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_openai.chat_models import ChatOpenAI
from langchain_huggingface import HuggingFacePipeline
from langchain_google_genai import ChatGoogleGenerativeAI
from weaviate.classes.query import MetadataQuery, Filter

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
            "filter_analyzer_template": [
                ChatPromptTemplate.from_template(filter_analyzer_template),
            ],
            "analyzer_template": [
                ChatPromptTemplate.from_template(analyzer_template),
            ],
            "chat_template": chat_template,
            "reask_template": reask_template,
            "building_found_template": building_found_template,
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
            max_retries=3,
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

    def receive_prompt(self, sessionid, prompt) -> Message:
        """ 
        Receive prompt, receive the prompt from the client app
        :param prompt: chat message to be analyzed.
        """
        self._logger.log_info(f"Session: {sessionid}")
        conversation = None
        if sessionid in self._store:
            conversation = self._store[sessionid]
            self._logger.log_info(conversation)
            
        templates = self._templates["analyzer_template"]
        result: str = self._prompt_parser.execute(
            {"prompts": prompt, "conversations": conversation if conversation else ""},
            templates
        )
        result = result.strip()
        
        # using string to avoid truthy context of boolean
        self._logger.log_info(f"Is asking for boarding house: {result}\n")
        if result == "True":
            templates = self._templates["filter_analyzer_template"]
            result: str = self._prompt_parser.execute(
                {"prompts": prompt, "conversations": conversation if conversation else ""},
                templates
            )
            
            self._logger.log_info(f"Filters: {result}\n")
            json_result = result.strip("`").strip("json").strip("`").strip()
            self._logger.log_info(f"Stripped: {json_result}\n")
            
            data_dict = json.loads(json_result)
            buildings_filter = BuildingsFilter(**data_dict)
            self._logger.log_info(f"Filters in Pydantic: {buildings_filter}\n")

            filter_array: list = []
            filter_array = append_housing_price_filters(buildings_filter, filter_array)
            self._logger.log_info(f"Filters array: {filter_array}\n")
            
            building_instance = None
            building_query = None
            if(buildings_filter.building_title is not None or buildings_filter.building_address is not None):
                building_instance  = Building(
                    building_title=buildings_filter.building_title,
                    building_address=buildings_filter.building_address,
                    building_description=buildings_filter.building_facility
                )
                building_dict = building_instance.to_dict()
                building_query = str(building_dict)
                
            building_query = prompt if building_query is None else building_query
            self._logger.log_info(f"Query: {building_query}\n")
            
            output = self.analyze_prompt(prompt, sessionid, filter_array, building_query)
            return output
        
        return self.feedback_prompt(prompt, sessionid)

    def analyze_prompt(self, prompt, sessionId, filter_array, query = "") -> Message:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        :param filter_array: filters that needed for prompt analysis.
        """
        buildings_collection = self._weaviate_client.collections.get(BUILDINGS_COLLECTION_NAME)
        response = buildings_collection.query.hybrid(
            query=query,
            target_vector="building_details",
            filters=Filter.all_of(filter_array) if len(filter_array) > 0 else None,
            limit=5,
            return_metadata=MetadataQuery(distance=True,certainty=True)
        )
        
        # if the len of the object is 0, reask the user about the prompt
        if(len(response.objects) == 0):
            output = self.feedback_prompt(prompt, sessionId, True)
            return output
            
        building_list: List[Building] = []
        for obj in response.objects:
            self._logger.log_info(f"Found object: {obj.properties}")
            data_dict = ast.literal_eval(str(obj.properties))
            building_instance = Building.from_dict(data_dict)
            building_list.append(building_instance)
            
            
        output = self.feedback_prompt(prompt, sessionId, found=building_list)
        return output

    def feedback_prompt(self, prompt, sessionId, reask = False, found = None) -> Message:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        :param reask: reask flag.
        """
        self._logger.log_info(f"Is reask for something is necessary: {reask}")
        self._logger.log_info(f"Is search found: {found}")
        
        template = self._templates["reask_template"] if reask else self._templates["chat_template"]
        if found:
            template = self._templates["building_found_template"]

        input_variables = ["prompts", "service_pic_number", "advertising_pic_number" , "result"]
        runnable_input = {
            "prompts": prompt,
            "service_pic_number": SERVICE_PIC_NUMBER,
            "advertising_pic_number": ADVERTISING_PIC_NUMBER
        }

        if found:
            runnable_input["result"] = found
            
        output = self.respond(template, input_variables, runnable_input, sessionId)
        return Message(
            input=prompt,
            output=output,
            output_content=found
        )

    def respond(self, template, input_variables, runnable_input, session_id) -> str:
        """ 
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        """
        system_message = SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template=template,
                input_variables=input_variables
            )
        )
        
        template = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="history"),
            ("human", "{prompts}"),
        ])
        
        chain = template | self._client | StrOutputParser()
        with_message_history = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="prompts",
            history_messages_key="history",
        )
        
        result: Runnable = with_message_history.invoke(
            runnable_input,
            config={"configurable": {"session_id": session_id}}
        )
        
        self._logger.log_info(f"AI Result: {result}")
        return result