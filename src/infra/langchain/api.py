""" Module for LangchainAPI
"""

# Standard and third-party libraries
import time
import json
import traceback

# Source-specific imports
from configs.config import (
    ADVERTISING_PIC_NUMBER, SERVICE_PIC_NUMBER,
    OPENAI_MODEL, HUGGINGFACE_MODEL, GEMINI_MODEL,
    GEMINI_API_KEY, USE_MODULE, MODULE_USED, OPENAI_ANALYZER_MODEL, OPENAI_FILTER_DATA_STRUCTURER_MODEL
)
from src.domain.entities.message.message import Message
from src.domain.constants import OPENAI, HUGGING_FACE, GEMINI, BUILDING_CHUNKS_COLLECTION_NAME, BUILDINGS_COLLECTION_NAME
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
from src.infra.repositories.weaviate.schema.collections.buildings.buildings import (
    append_housing_price_filters,
    append_building_facility_filters,
    append_building_note_filters,
    append_building_geolocation_filters
)
from src.domain.entities.building.building import Building
from src.infra.geocoding.api import GeocodingAPI

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

# Weaviate
from src.infra.repositories.weaviate.query.query import query_building_with_building_as_reference, query_building
from weaviate.classes.query import Filter

class LangchainAPI(LangchainAPIInterface):
    """ LangchainAPI class.
    """

    def __init__(self, llm_type: str, api_key: str, logger: LoggerInterface) -> None: 
        self._api_key = api_key
        self._logger = logger
        self._store = {}
        
        self.init_llm(llm_type)
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._logger.log_exception(f"[{exc_type}]: {exc_val}")
            self._logger.log_exception(f"Traceback: {traceback.format_tb(exc_tb)}")
        
    def init_llm(self, llm_type) -> None:
        if llm_type == OPENAI:
            print(OPENAI_MODEL)
            print(OPENAI_ANALYZER_MODEL)
            print(OPENAI_FILTER_DATA_STRUCTURER_MODEL)
            self._client = self.create_open_ai_llm(OPENAI_MODEL)
            self._analyzer_client = self.create_open_ai_llm(OPENAI_ANALYZER_MODEL)
            self._filter_data_structurer_client = self.create_open_ai_llm(OPENAI_FILTER_DATA_STRUCTURER_MODEL)
        elif llm_type == HUGGING_FACE:
            self._client = self.create_huggingface_llm(HUGGINGFACE_MODEL)
            self._analyzer_client = self.create_huggingface_llm(HUGGINGFACE_MODEL)
            self._filter_data_structurer_client = self.create_open_ai_llm(HUGGINGFACE_MODEL)
        elif llm_type == GEMINI:
            self._client = self.create_gemini_llm(GEMINI_MODEL)
            self._analyzer_client = self.create_huggingface_llm(GEMINI_MODEL)
            self._filter_data_structurer_client = self.create_open_ai_llm(GEMINI_MODEL)
        else:
            raise Exception("No LLM Found")
        
        self._prompt_parser = PromptParser(self._client)
        self._analyzer_prompt_parser = PromptParser(self._analyzer_client)
        self._filter_data_structurer_prompt_parser = PromptParser(self._filter_data_structurer_client)

    def create_open_ai_llm(self, llm_model) -> ChatOpenAI:
        """ 
        Create OpenAI LLM and register it as dependency
        """
        client = ChatOpenAI(model=llm_model, api_key=self._api_key)
        return client
        
    def create_gemini_llm(self, llm_model) -> ChatGoogleGenerativeAI:
        """ 
        Create Gemini LLM and register it as dependency
        """
        baseUrl = 'https://generativelanguage.googleapis.com'
        version = 'v1beta'
        client = ChatGoogleGenerativeAI(
            model=llm_model,
            google_api_key=GEMINI_API_KEY,
            temperature=0,
            baseUrl=baseUrl,
            max_retries=3,
            version=version
        )
        return client
        
    def create_huggingface_llm(self, llm_model) -> HuggingFacePipeline:
        """ 
        Create Huggingface LLM and register it as dependency
        """
        # NOTE 
        # doesn't support Bahasa Indonesia 
        client = HuggingFacePipeline.from_model_id(
            model_id=llm_model,
            task="text-generation",
            pipeline_kwargs={
                "max_new_tokens": 100,
                "top_k": 50,
                "temperature": 0.1,
            },
        )
        return client

    def get_session_history(self, session_id) -> BaseChatMessageHistory:
        """ Get message history by session id
        :param session_id: chat session id
        :return: BaseChatMessageHistory
        """
        if session_id not in self._store:
            self._store[session_id] = ChatMessageHistory()
        return self._store[session_id]

    def analyze_prompt(self, session_id, prompt) -> Message:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param session_id: chat session id.
        :param prompt: chat message to be analyzed.
        """
        self._logger.log_info(f"Session: {session_id}")
        self._logger.log_info(f"User prompt: {prompt}")
        conversation = None
        if session_id in self._store:
            conversation = self._store[session_id]
            # Only let 10 message in the chat history for context window efficiency
            while len(self._store[session_id].messages) > 10:
                self._store[session_id].messages.pop(0)
            self._logger.log_info(f"\n---------------------------conversation of user {session_id}---------------------------")
            self._logger.log_info(conversation)
            self._logger.log_info(f"\n---------------------------end of conversation user {session_id}---------------------------")
            
        templates = self._templates["analyzer_template"]
        result: str = self._analyzer_prompt_parser.execute(
            {"prompts": prompt, "conversations": conversation if conversation else ""},
            templates
        )
        result = result.strip()
        
        # using string to avoid truthy context of boolean
        self._logger.log_info(f"Is asking for boarding house: {result}")
        if result == "True":
            templates = self._templates["filter_analyzer_template"]
            result: str = self._filter_data_structurer_prompt_parser.execute(
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
                "housing_price" : lambda with_reference: append_housing_price_filters(buildings_filter, [], with_reference),
                "building_facility" : append_building_facility_filters(buildings_filter, []),
                "building_note" : append_building_note_filters(buildings_filter, []),
            }
            
            building_instance = None
            location_query = None
            facility_query = None
            
            if(any([
                buildings_filter.building_title,
                buildings_filter.building_address,
                buildings_filter.building_proximity,
            ])):
                building_instance = Building(
                    building_title=buildings_filter.building_title,
                    building_address=buildings_filter.building_address,
                    building_proximity=buildings_filter.building_proximity,
                ) 
                location_query = self._query_parser.execute(building_instance.to_dict())
                
            with GeocodingAPI(self._logger) as obj:
                try:
                    if(location_query is not None):
                        geocode_data = obj.execute_geocode_by_address(location_query)
                        self._logger.log_info(f"Got geocode data: {geocode_data}")
                        if (len(geocode_data) > 0):
                            lat_long = geocode_data[0]['geometry']['location']
                            filter_array["building_geolocation"] = lambda distance: append_building_geolocation_filters(lat_long, distance , [])    
                except Exception as e:
                    self._logger.log_exception(f"Error Geocode: {e}")
            
            if(any([
                buildings_filter.building_title,
                buildings_filter.building_facility,
                buildings_filter.building_note
            ])):
                facility_query_instance = Building(
                    building_title=buildings_filter.building_title,
                    building_facility=buildings_filter.building_facility,
                    building_note=buildings_filter.building_note,
                )       
                facility_query = self._query_parser.execute(facility_query_instance.to_dict())
            
            self._logger.log_info(f"Facility Query:{facility_query}")
            self._logger.log_info(f"Location Query:{location_query}")
            output = self.vector_db_retrieval(prompt, session_id, filter_array, facility_query, location_query)
            return output
        
        return self.feedback_prompt(prompt, session_id)

    def vector_db_retrieval(self, prompt, session_id, filter_array, facility_query="", location_query="") -> Message:
        """
        Vector database data retrieval process
        :param prompt: chat message to be analyzed.
        :param session_id: session id of the chat.
        :param filter_array: filters that needed for prompt analysis.
        :param query: query for vector data retrieval with weaviate.
        """
        response = None
        limit = 10
        offset = 0
        start_time = time.time()
        building_list: list[Building] = []
        seen_uuids = set()
        retries = 0
        max_retries = 3
        
        # Geolocation radius stages
        # Add more stages to use multiple stages
        geolocation_stages = [6000]
        geolocation_stage_index = 0
        
        # Setup fixed filters
        chunk_collection_filters = None
        if len(filter_array["building_facility"]) > 0:
            chunk_collection_filters = Filter.any_of(filter_array["building_facility"])
        if len(filter_array["building_note"]) > 0:
            chunk_collection_filters = chunk_collection_filters & Filter.any_of(filter_array["building_note"]) if chunk_collection_filters else Filter.any_of(filter_array["building_note"])    
        
        with WeaviateAPI(self._logger) as weaviate_client:
            while retries < max_retries:
                try:
                    connected = weaviate_client.connect_to_server(int(USE_MODULE), MODULE_USED)
                    building_collection = connected.collections.get(BUILDINGS_COLLECTION_NAME)
                    building_chunk_collection = connected.collections.get(BUILDING_CHUNKS_COLLECTION_NAME)
                    is_geofilter_callable = callable(filter_array.get("building_geolocation"))
                    
                    while len(building_list) < limit:
                        filters = None
                        with_geofilter = is_geofilter_callable and geolocation_stage_index < len(geolocation_stages)
                        
                        if with_geofilter:
                            housing_price_filter = filter_array["housing_price"](False)
                            if len(housing_price_filter) > 0:
                                filters = Filter.all_of(housing_price_filter)
                                
                            distance = geolocation_stages[geolocation_stage_index]
                            geofilter = filter_array["building_geolocation"](distance)
                            filters = filters & Filter.any_of(geofilter) if filters else Filter.any_of(geofilter)
                            
                            self._logger.log_info(f"Execute query with facility query: {facility_query}")
                            self._logger.log_info(f"Trying to get location at: {distance} distance")
                            self._logger.log_info(f"Executing with filters: {filters}")
                            response = query_building(
                                building_collection,
                                facility_query,
                                filters,
                                limit,
                                offset
                            )
                        else:
                            housing_price_filter = filter_array["housing_price"](True)
                            if len(housing_price_filter) > 0:
                                filters = Filter.all_of(housing_price_filter)
                            filters = filters & chunk_collection_filters if chunk_collection_filters else filters
                                
                            self._logger.log_info(f"Execute query with location query: {location_query}")
                            self._logger.log_info(f"Executing with filters: {filters}")
                            response = query_building_with_building_as_reference(
                                building_chunk_collection,
                                location_query,
                                filters,
                                limit,
                                offset
                            )
                        
                        if not response.objects:
                            if with_geofilter:
                                self._logger.log_info(f"Failed to get location at: {distance} distance, with query {facility_query}")
                                geolocation_stage_index += 1
                                offset = 0
                            else:
                                self._logger.log_info(f"Failed to get location with query: {location_query}")
                                break

                        self._logger.log_info(f"Queried object found count: {len(response.objects)}")
                        for obj in response.objects:
                            if with_geofilter:
                                self._logger.log_info(f"[{obj.uuid}]: Adding building {obj.properties["buildingTitle"]}")
                                seen_uuids.add(obj.uuid)
                                building_instance = Building(
                                    building_title=obj.properties["buildingTitle"],
                                    building_address=obj.properties["buildingAddress"],
                                    building_description=obj.properties["buildingDescription"],
                                    housing_price=obj.properties["housingPrice"],
                                    owner_name=obj.properties["ownerName"],
                                    owner_email=obj.properties["ownerEmail"],
                                    owner_whatsapp=obj.properties["ownerWhatsapp"],
                                    owner_phone_number=obj.properties["ownerPhoneNumber"],
                                    image_url=obj.properties["imageURL"]
                                )
                                building_list.append(building_instance)
                                self._logger.log_info(f"Building object added, length: {len(building_list)}")
                            else:
                                for ref_obj in obj.references["hasBuilding"].objects:
                                    if ref_obj.uuid in seen_uuids:
                                        continue

                                    self._logger.log_info(f"[{ref_obj.uuid}]: Adding building {ref_obj.properties["buildingTitle"]}")
                                    seen_uuids.add(ref_obj.uuid)
                                    building_instance = Building(
                                        building_title=ref_obj.properties["buildingTitle"],
                                        building_address=ref_obj.properties["buildingAddress"],
                                        building_description=ref_obj.properties["buildingDescription"],
                                        housing_price=ref_obj.properties["housingPrice"],
                                        owner_name=ref_obj.properties["ownerName"],
                                        owner_email=ref_obj.properties["ownerEmail"],
                                        owner_whatsapp=ref_obj.properties["ownerWhatsapp"],
                                        owner_phone_number=ref_obj.properties["ownerPhoneNumber"],
                                        image_url=ref_obj.properties["imageURL"]
                                    )
                                    building_list.append(building_instance)
                                    self._logger.log_info(f"Building object added, length: {len(building_list)}")
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
                    if retries == max_retries:
                        self._logger.log_exception(f"Weaviate operation failed after {max_retries} retries.")
                    else:
                        self._logger.log_warning(f"Attempt {retries} failed: {e}. Retrying...")
                        retries += 1
                finally:
                    weaviate_client.close_connection_to_server(connected)
                
        if len(building_list) == 0:
            output = self.feedback_prompt(prompt, session_id, True)
        else:
            output = self.feedback_prompt(prompt, session_id, found=building_list)
            
        return output

    def feedback_prompt(self, prompt, session_id, reask = False, found = None) -> Message:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        :param session_id: session id of the chat.
        :param reask: reask flag.
        :param found: data found elements.
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
        :param template: chat prompt template.
        :param input_variables: input variables for the prompt template.
        :param runnable_input: list of runnable template for langchain pipe.
        :param session_id: session id of the chat.
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
