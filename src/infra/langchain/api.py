""" Module for LangchainAPI
"""

# Standard and third-party libraries
import time
import json
import traceback

# Source-specific imports
from configs.config import (
    ADVERTISING_PIC_NUMBER,
    SERVICE_PIC_NUMBER,
    OPENAI_MODEL,
    GEMINI_MODEL,
    GEMINI_API_KEY,
    USE_MODULE,
    MODULE_USED,
    OPENAI_API_KEY,
    OPENAI_ANALYZER_MODEL,
    OPENAI_FILTER_DATA_STRUCTURER_MODEL,
)
from src.domain.entities.message.message import Message
from src.domain.constants import (
    OPENAI,
    GEMINI,
    BUILDING_CHUNKS_COLLECTION_NAME,
    BUILDINGS_COLLECTION_NAME,
)
from src.domain.prompt_templates import (
    chat_template,
    analyzer_template,
    filter_data_structurer_analyzer_template,
    reask_template,
    building_found_template,
)
from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter
from src.infra.langchain.prompt_parser.prompt_parser import PromptParser
from langchain_community.chat_message_histories import ChatMessageHistory
from src.infra.langchain.llm.llm import create_open_ai_llm, create_gemini_llm
from src.interactor.interfaces.langchain.api import LangchainAPIInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.repositories.weaviate.schema.collections.buildings.buildings import (
    append_housing_price_filters,
    append_building_facility_filters,
    append_building_note_filters,
    append_building_geolocation_filters,
)
from src.domain.entities.building.building import Building
from src.infra.geocoding.api import GeocodingAPI

# Langchain and related libraries
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory

# Weaviate
from src.infra.repositories.weaviate.api import WeaviateAPI
from src.infra.repositories.weaviate.query_parser.query_parser import QueryParser
from src.infra.repositories.weaviate.query.query import (
    query_building_with_building_as_reference,
    query_building,
)
from weaviate.classes.query import Filter


class LangchainAPI(LangchainAPIInterface):
    """LangchainAPI class."""

    def __init__(self, llm_type: str, logger: LoggerInterface) -> None:
        self._logger = logger
        self._store = {}
        self._llm_type = llm_type
        self._client = None
        self._analyzer_client = None
        self._filter_data_structurer_client = None
        self._query_parser = QueryParser()
        self._templates = {
            "filter_data_structurer_analyzer_template": [
                ChatPromptTemplate.from_template(filter_data_structurer_analyzer_template),
            ],
            "analyzer_template": [
                ChatPromptTemplate.from_template(analyzer_template),
            ],
            "chat_template": chat_template,
            "reask_template": reask_template,
            "building_found_template": building_found_template,
        }

        self.connect_llm()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._logger.log_error(f"[{exc_type}]: {exc_val}")
            self._logger.log_error(f"Traceback: {traceback.format_tb(exc_tb)}")

    def connect_llm(self) -> None:
        """
        Connect selected LLM and initialize prompt parsers
        """
        try:
            if not self._client:
                if self._llm_type == OPENAI:
                    self._client = create_open_ai_llm(OPENAI_MODEL, OPENAI_API_KEY)
                    self._analyzer_client = create_open_ai_llm(
                        OPENAI_ANALYZER_MODEL, OPENAI_API_KEY
                    )
                    self._filter_data_structurer_client = create_open_ai_llm(
                        OPENAI_FILTER_DATA_STRUCTURER_MODEL, OPENAI_API_KEY
                    )
                elif self._llm_type == GEMINI:
                    self._client = create_gemini_llm(GEMINI_MODEL, GEMINI_API_KEY)
                    self._analyzer_client = create_gemini_llm(
                        GEMINI_MODEL, GEMINI_API_KEY
                    )
                    self._filter_data_structurer_client = create_gemini_llm(
                        GEMINI_MODEL, GEMINI_API_KEY
                    )
                else:
                    raise ValueError("No LLM Found")

                self._prompt_parser = PromptParser(self._client)
                self._analyzer_prompt_parser = PromptParser(self._analyzer_client)
                self._filter_data_structurer_prompt_parser = PromptParser(
                    self._filter_data_structurer_client
                )
        except Exception as e:
            self._logger.log_exception(f"Error connecting LLM: {e}")

    def get_session_history(self, session_id) -> BaseChatMessageHistory:
        """Get message history by session id
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
        self._logger.log_info(f"[{session_id}]: User prompt: {prompt}")
        conversation = None
        if session_id in self._store:
            conversation = self._store[session_id]
            # Only let 10 message in the chat history for context window efficiency
            while len(self._store[session_id].messages) > 10:
                self._store[session_id].messages.pop(0)
            self._logger.log_info(
                f"---------------------------conversation of user {session_id}---------------------------\n{conversation}\n---------------------------end of conversation user {session_id}---------------------------"
            )

        templates = self._templates["analyzer_template"]
        result: str = self._analyzer_prompt_parser.execute(
            {"prompts": prompt, "conversations": conversation if conversation else ""},
            templates,
        )
        result = result.strip()

        # using string to avoid truthy context of boolean
        self._logger.log_info(f"[{session_id}]: Is asking for boarding house: {result}")
        if result == "True":
            templates = self._templates["filter_data_structurer_analyzer_template"]
            result: str = self._filter_data_structurer_prompt_parser.execute(
                {
                    "prompts": prompt,
                    "conversations": conversation if conversation else "",
                },
                templates,
            )

            json_result = result.strip("`").strip("json").strip("`").strip()
            data_dict = json.loads(json_result)
            buildings_filter = BuildingsFilter(**data_dict)
            self._logger.log_debug(f"[{session_id}]: Filters - {buildings_filter}")

            filter_array = None
            filter_array = {
                "housing_price": lambda with_reference: append_housing_price_filters(
                    buildings_filter, [], with_reference
                ),
                "building_facility": append_building_facility_filters(
                    buildings_filter, []
                ),
                "building_note": append_building_note_filters(buildings_filter, []),
            }

            building_instance = None
            with GeocodingAPI(self._logger) as obj:
                try:
                    query = (
                        buildings_filter.building_title
                        if buildings_filter.building_title
                        else buildings_filter.building_proximity
                    )
                    if query is not None:
                        geocode_data = obj.execute_geocode_by_address(query)
                        if len(geocode_data) > 0:
                            self._logger.log_debug(
                                f"[{session_id}]: Got geocode data: {geocode_data}"
                            )
                            lat_long = geocode_data[0]["geometry"]["location"]
                            filter_array["building_geolocation"] = (
                                lambda distance: append_building_geolocation_filters(
                                    lat_long, distance, []
                                )
                            )
                except Exception as e:
                    self._logger.log_exception(f"[{session_id}]: Error Geocode: {e}")

            location_query = None
            facility_query = None
            if any(
                [
                    buildings_filter.building_title,
                    buildings_filter.building_address,
                    buildings_filter.building_proximity,
                ]
            ):
                building_instance = Building(
                    building_title=buildings_filter.building_title,
                    building_address=buildings_filter.building_address,
                    building_proximity=buildings_filter.building_proximity,
                )
                location_query = self._query_parser.execute(building_instance.to_dict())
                self._logger.log_debug(
                    f"[{session_id}]: Location Query:{location_query}"
                )

            if any(
                [
                    buildings_filter.building_title,
                    buildings_filter.building_facility,
                    buildings_filter.building_note,
                ]
            ):
                facility_query_instance = Building(
                    building_title=buildings_filter.building_title,
                    building_facility=buildings_filter.building_facility,
                    building_note=buildings_filter.building_note,
                )
                facility_query = self._query_parser.execute(
                    facility_query_instance.to_dict()
                )
                self._logger.log_debug(
                    f"[{session_id}]: Facility Query:{facility_query}"
                )

            output = self.vector_db_retrieval(
                prompt, session_id, filter_array, facility_query, location_query
            )
            return output

        return self.feedback_prompt(prompt, session_id)

    def vector_db_retrieval(
        self, prompt, session_id, filter_array, facility_query="", location_query=""
    ) -> Message:
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
        geolocation_stages = [5000]
        geolocation_stage_index = 0

        # Setup fixed filters
        chunk_collection_filters = None
        if len(filter_array["building_facility"]) > 0:
            chunk_collection_filters = Filter.any_of(filter_array["building_facility"])
        if len(filter_array["building_note"]) > 0:
            chunk_collection_filters = (
                chunk_collection_filters & Filter.any_of(filter_array["building_note"])
                if chunk_collection_filters
                else Filter.any_of(filter_array["building_note"])
            )

        with WeaviateAPI(self._logger) as weaviate_client:
            while retries < max_retries:
                try:
                    connected = weaviate_client.connect_to_server(
                        int(USE_MODULE), MODULE_USED
                    )
                    building_collection = connected.collections.get(
                        BUILDINGS_COLLECTION_NAME
                    )
                    building_chunk_collection = connected.collections.get(
                        BUILDING_CHUNKS_COLLECTION_NAME
                    )
                    is_geofilter_callable = callable(
                        filter_array.get("building_geolocation")
                    )

                    while len(building_list) < limit:
                        filters = None
                        with_geofilter = (
                            is_geofilter_callable
                            and geolocation_stage_index < len(geolocation_stages)
                        )

                        if with_geofilter:
                            housing_price_filter = filter_array["housing_price"](False)
                            if len(housing_price_filter) > 0:
                                filters = Filter.all_of(housing_price_filter)

                            distance = geolocation_stages[geolocation_stage_index]
                            geofilter = filter_array["building_geolocation"](distance)
                            filters = (
                                filters & Filter.any_of(geofilter)
                                if filters
                                else Filter.any_of(geofilter)
                            )

                            self._logger.log_info(
                                f"[{session_id}]: Execute with facility query: {facility_query}\nLocation at: {distance}\nFilters: {filters}"
                            )
                            response = query_building(
                                building_collection,
                                facility_query,
                                filters,
                                limit,
                                offset,
                            )
                        else:
                            housing_price_filter = filter_array["housing_price"](True)
                            if len(housing_price_filter) > 0:
                                filters = Filter.all_of(housing_price_filter)

                            if filters and chunk_collection_filters:
                                filters = filters & chunk_collection_filters
                            elif not filters:
                                filters = chunk_collection_filters

                            self._logger.log_info(
                                f"[{session_id}]: Execute with location query: {location_query}\nFilters: {filters}"
                            )
                            response = query_building_with_building_as_reference(
                                building_chunk_collection,
                                location_query,
                                filters,
                                limit,
                                offset,
                            )

                        if not response.objects:
                            if with_geofilter:
                                self._logger.log_debug(
                                    f"[{session_id}]: Failed to get location at: {distance} distance, with query {facility_query}"
                                )
                                geolocation_stage_index += 1
                                offset = 0
                            else:
                                self._logger.log_debug(
                                    f"[{session_id}]: Failed to get location with query: {location_query}"
                                )
                                break

                        self._logger.log_debug(
                            f"[{session_id}]: Queried object found count: {len(response.objects)}"
                        )
                        for obj in response.objects:
                            if with_geofilter:
                                seen_uuids.add(obj.uuid)
                                building_instance = Building(
                                    building_title=obj.properties["buildingTitle"],
                                    building_address=obj.properties["buildingAddress"],
                                    building_description=obj.properties[
                                        "buildingDescription"
                                    ],
                                    housing_price=obj.properties["housingPrice"],
                                    owner_name=obj.properties["ownerName"],
                                    owner_email=obj.properties["ownerEmail"],
                                    owner_whatsapp=obj.properties["ownerWhatsapp"],
                                    owner_phone_number=obj.properties[
                                        "ownerPhoneNumber"
                                    ],
                                    image_url=obj.properties["imageURL"],
                                )
                                building_list.append(building_instance)
                            else:
                                for ref_obj in obj.references["hasBuilding"].objects:
                                    if ref_obj.uuid in seen_uuids:
                                        continue

                                    seen_uuids.add(ref_obj.uuid)
                                    building_instance = Building(
                                        building_title=ref_obj.properties[
                                            "buildingTitle"
                                        ],
                                        building_address=ref_obj.properties[
                                            "buildingAddress"
                                        ],
                                        building_description=ref_obj.properties[
                                            "buildingDescription"
                                        ],
                                        housing_price=ref_obj.properties[
                                            "housingPrice"
                                        ],
                                        owner_name=ref_obj.properties["ownerName"],
                                        owner_email=ref_obj.properties["ownerEmail"],
                                        owner_whatsapp=ref_obj.properties[
                                            "ownerWhatsapp"
                                        ],
                                        owner_phone_number=ref_obj.properties[
                                            "ownerPhoneNumber"
                                        ],
                                        image_url=ref_obj.properties["imageURL"],
                                    )
                                    building_list.append(building_instance)
                                    if len(building_list) >= limit:
                                        break

                            if len(building_list) >= limit:
                                break

                        offset += limit

                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self._logger.log_info(
                        f"[{session_id}]: Time taken to execute query and process results: {elapsed_time} seconds.\nTotal object count: {str(len(building_list))}"
                    )
                    break
                except Exception as e:
                    if retries == max_retries:
                        self._logger.log_exception(
                            f"[{session_id}]: Failed do weaviate query, ERROR: {e}\nWeaviate operation failed after {max_retries} retries."
                        )
                    else:
                        self._logger.log_warning(
                            f"[{session_id}]: Failed do weaviate query, ERROR: {e}\nAttempt {retries} failed: {e}."
                        )
                        retries += 1
                finally:
                    weaviate_client.close_connection_to_server(connected)

        if len(building_list) == 0:
            output = self.feedback_prompt(prompt, session_id, True)
        else:
            output = self.feedback_prompt(prompt, session_id, found=building_list)

        return output

    def feedback_prompt(self, prompt, session_id, reask=False, found=None) -> Message:
        """
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        :param session_id: session id of the chat.
        :param reask: reask flag.
        :param found: data found elements.
        """
        self._logger.log_info(
            f"[{session_id}]: Is reask for something is necessary: {reask}\nIs search found: {True if found else False}"
        )
        template = (
            self._templates["reask_template"]
            if reask
            else self._templates["chat_template"]
        )
        if found:
            template = self._templates["building_found_template"]

        input_variables = [
            "prompts",
            "service_pic_number",
            "advertising_pic_number",
            "result",
        ]
        runnable_input = {
            "prompts": prompt,
            "service_pic_number": SERVICE_PIC_NUMBER,
            "advertising_pic_number": ADVERTISING_PIC_NUMBER,
        }

        if found:
            runnable_input["result"] = found

        output = self.respond(template, input_variables, runnable_input, session_id)
        return Message(input=prompt, output=output, output_content=found)

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
            prompt=PromptTemplate(template=template, input_variables=input_variables)
        )

        template = ChatPromptTemplate.from_messages(
            [
                system_message,
                MessagesPlaceholder(variable_name="history"),
                ("human", "{prompts}"),
            ]
        )

        chain = template | self._client | StrOutputParser()
        with_message_history = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="prompts",
            history_messages_key="history",
        )

        result: Runnable = with_message_history.invoke(
            runnable_input, config={"configurable": {"session_id": session_id}}
        )

        return result
