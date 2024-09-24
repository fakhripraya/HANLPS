""" Module for LangchainAPI
"""

# Standard and third-party libraries
import time
import json
import socket

# Source-specific imports
from configs.config import (
    ADVERTISING_PIC_NUMBER, SERVICE_PIC_NUMBER,
    OPENAI_MODEL, HUGGINGFACE_MODEL, GEMINI_MODEL,
    GEMINI_API_KEY, USE_MODULE, MODULE_USED
)
from src.domain.entities.message.message import Message
from src.domain.constants import OPENAI, HUGGING_FACE, GEMINI, BUILDING_CHUNKS_COLLECTION_NAME
from src.domain.prompt_templates import (
    chat_template,
    analyzer_template,
    filter_analyzer_template,
    reask_template,
    building_found_template
)
from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter
from src.infra.langchain.prompt_parser.prompt_parser import PromptParser
from src.infra.repositories.weaviate.query_parser.query_parser import QueryParser
from src.infra.repositories.weaviate.api import WeaviateAPI
from src.interactor.interfaces.langchain.api import LangchainAPIInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.repositories.weaviate.schema.collections.buildings.buildings import append_housing_price_filters, append_building_facility_filters, append_building_note_filters
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
from weaviate.classes.query import Filter
from weaviate.classes.query import QueryReference

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
        
        WeaviateAPI.__init__(self, int(USE_MODULE), MODULE_USED, self._logger)
        self._prompt_parser = PromptParser(self._client)
        self._query_parser = QueryParser()
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

    def get_session_history(self, session_id) -> BaseChatMessageHistory:
        """ Get message history by session id

        :param session_id: session id
        :return: BaseChatMessageHistory
        """
        if session_id not in self._store:
            self._store[session_id] = ChatMessageHistory()
        return self._store[session_id]

    def receive_prompt(self, session_id, prompt) -> Message:
        """ 
        Receive prompt, receive the prompt from the client app
        :param prompt: chat message to be analyzed.
        """
        self._logger.log_info(f"Session: {session_id}")
        self._logger.log_info(f"User prompt: {prompt}")
        conversation = None
        if session_id in self._store:
            conversation = self._store[session_id]
            self._logger.log_info(conversation)
            
        templates = self._templates["analyzer_template"]
        result: str = self._prompt_parser.execute(
            {"prompts": prompt, "conversations": conversation if conversation else ""},
            templates
        )
        result = result.strip()
        
        # using string to avoid truthy context of boolean
        self._logger.log_info(f"Is asking for boarding house: {result}")
        if result == "True":
            templates = self._templates["filter_analyzer_template"]
            result: str = self._prompt_parser.execute(
                {"prompts": prompt, "conversations": conversation if conversation else ""},
                templates
            )
            
            self._logger.log_info(f"Filters: {result}")
            json_result = result.strip("`").strip("json").strip("`").strip()
            self._logger.log_info(f"Stripped: {json_result}")
            
            data_dict = json.loads(json_result)
            buildings_filter = BuildingsFilter(**data_dict)
            self._logger.log_info(f"Filters in Pydantic: {buildings_filter}")

            filter_array = None
            filter_array = {
                "housing_price" : append_housing_price_filters(buildings_filter, []),
                "building_facility" : append_building_facility_filters(buildings_filter, []),
                "building_note" : append_building_note_filters(buildings_filter, [])
            }
            self._logger.log_info(f"Filters array: {filter_array}")
            
            building_instance = None
            building_query = None
            filter_validation = any([
                buildings_filter.building_title,
                buildings_filter.building_address,
                buildings_filter.building_proximity,
                # buildings_filter.building_facility
            ])
            if(filter_validation):
                building_instance = Building(
                    building_title=buildings_filter.building_title,
                    building_address=buildings_filter.building_address,
                    building_proximity=buildings_filter.building_proximity,
                    # building_facility=buildings_filter.building_facility
                )
                building_dict = building_instance.to_dict()
                building_query = self._query_parser.execute(building_dict)
            
            self._logger.log_info(f"Query:{building_query}")
            output = self.analyze_prompt(prompt, session_id, filter_array, building_query)
            return output
        
        return self.feedback_prompt(prompt, session_id)

    def analyze_prompt(self, prompt, session_id, filter_array, query="") -> Message:
        """
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        :param filter_array: filters that needed for prompt analysis.
        """
        response = None
        limit = 10
        offset = 0
        start_time = time.time()
        building_list: list[Building] = []
        seen_uuids = set()
        retries = 0
        max_retries = 3
        retry_delay_in_sec = 1
        while retries < max_retries:
            try:
                self._weaviate_client = WeaviateAPI.connect_to_server(self, int(USE_MODULE), MODULE_USED)
                building_chunk_collection = self._weaviate_client.collections.get(BUILDING_CHUNKS_COLLECTION_NAME)

                filters = None
                if len(filter_array["housing_price"]) > 0:
                    filters = Filter.all_of(filter_array["housing_price"])
                if len(filter_array["building_facility"]) > 0:
                    filters = filters & Filter.any_of(filter_array["building_facility"]) if filters else Filter.any_of(filter_array["building_facility"])
                if len(filter_array["building_note"]) > 0:
                    filters = filters & Filter.any_of(filter_array["building_note"]) if filters else Filter.any_of(filter_array["building_note"])
                
                while len(building_list) < limit:
                    self._logger.log_info("Execute query")
                    response = building_chunk_collection.query.hybrid(
                        query=query,
                        target_vector="buildingDetails",
                        filters=filters,
                        limit=limit,
                        offset=offset,
                        return_references=[
                            QueryReference(
                                include_vector=True,
                                link_on="hasBuilding"
                            ),
                        ],
                    )

                    self._logger.log_info(f"Object count: {len(response.objects)}")
                    if not response.objects:
                        break

                    for obj in response.objects:
                        self._logger.log_info(f"[Object {obj.uuid}]: {obj.properties['chunk']}")
                        for ref_obj in obj.references["hasBuilding"].objects:
                            if ref_obj.uuid in seen_uuids:
                                continue

                            seen_uuids.add(ref_obj.uuid)
                            building_instance = Building(
                                building_title=ref_obj.properties["buildingTitle"],
                                building_address=ref_obj.properties["buildingAddress"],
                                building_description=ref_obj.properties["buildingDescription"],
                                housing_price=ref_obj.properties["housingPrice"],
                                owner_name=ref_obj.properties["ownerName"],
                                owner_email=ref_obj.properties["ownerEmail"],
                                #owner_whatsapp=ref_obj.properties["ownerWhatsapp"],
                                #owner_phone_number=ref_obj.properties["ownerPhoneNumber"],
                                image_url=ref_obj.properties["imageURL"]
                            )
                            building_list.append(building_instance)
                            self._logger.log_info(f"Building instance added, length: {len(building_list)}")
                            if len(building_list) >= limit:
                                break
                    
                        if len(building_list) >= limit:
                            break
                        
                    offset += limit 
                
                end_time = time.time()
                elapsed_time = end_time - start_time
                self._logger.log_info(f"Time taken to execute query and process results: {elapsed_time} seconds.\nTotal object count: {str(len(building_list))}")
                break
            except Exception as e:
                self._logger.log_exception(f"Failed do weaviate query, ERROR: {e}")
                print(f"Attempt {retries} failed: {e}. Retrying in {retry_delay_in_sec} seconds...")
                retries += 1
                time.sleep(retry_delay_in_sec)
            finally:
                WeaviateAPI.close_connection_to_server(self)
        else:
            print(f"Weaviate operation failed after {max_retries} retries.")
            
        if len(building_list) == 0:
            output = self.feedback_prompt(prompt, session_id, True)
        else:
            output = self.feedback_prompt(prompt, session_id, found=building_list)
            
        return output

    def feedback_prompt(self, prompt, session_id, reask = False, found = None) -> Message:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        :param reask: reask flag.
        """
        self._logger.log_info(f"Is reask for something is necessary: {reask}")
        self._logger.log_info(f"Is search found: {True if found else False}")
        
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
            
        output = self.respond(template, input_variables, runnable_input, session_id)
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