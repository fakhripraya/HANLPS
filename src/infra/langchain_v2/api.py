""" Module for LangchainAPIV2
"""

# Standard and third-party libraries
import time
import traceback

# Source-specific imports
from configs.config import (
    ADVERTISING_PIC_NUMBER,
    SERVICE_PIC_NUMBER,
    USE_MODULE,
    MODULE_USED,
)
from src.domain.entities.message.message import Message
from src.domain.constants import (
    BUILDINGS_COLLECTION_NAME,
    BUILDING_CHUNKS_COLLECTION_NAME,
)
from src.domain.prompt_templates import (
    default_reply_template,
    filter_data_structurer_analyzer_template,
    reask_template,
    seen_buildings_template,
    building_object_template,
    building_found_template,
    location_verifier_template,
)
from src.domain.constants import RETRIEVE_BOARDING_HOUSES_OR_BUILDINGS
from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter
from src.domain.entities.building.building import Building
from src.infra.langchain_v2.agent.agent import create_agent
from src.infra.langchain_v2.tools.tools import tools
from src.infra.langchain_v2.memory.memory import LimitedConversationBufferMemory
from src.infra.geocoding.api import GeocodingAPI
from src.infra.repositories.weaviate.filters.buildings.buildings import (
    append_housing_price_filters,
    append_building_facility_filters,
    append_building_note_filters,
    append_building_geolocation_filter,
)
from src.interactor.interfaces.langchain_v2.api import LangchainAPIV2Interface
from src.interactor.interfaces.logger.logger import LoggerInterface

# Langchain and related libraries
from langchain.agents import AgentExecutor
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser

# Weaviate
from src.infra.repositories.weaviate.api import WeaviateAPI
from src.infra.repositories.weaviate.query.query import (
    query_building_with_building_as_reference,
    query_building,
)
from weaviate.classes.query import Filter
from weaviate.collections.collection import CrossReferences
from weaviate.collections.classes.types import WeaviateProperties
from weaviate.collections.classes.internal import QueryReturn, Object


class LangchainAPIV2(LangchainAPIV2Interface):
    """LangchainAPIV2 class."""

    def __init__(self, llm_type: str, logger: LoggerInterface) -> None:
        self._logger = logger
        self._store = {}
        self._agent = create_agent(llm_type, logger)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._logger.log_error(f"[{exc_type}]: {exc_val}")
            self._logger.log_error(f"Traceback: {traceback.format_tb(exc_tb)}")

    def clear_messaging_history(self, session_id) -> bool:
        """
        Clear message history
        :param session_id: chat session id.
        """
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False

    def analyze_prompt(self, session_id, prompt) -> Message:
        """
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param session_id: chat session id.
        :param prompt: chat message to be analyzed.
        """
        self._logger.log_info(f"[{session_id}]: User prompt: {prompt}")

        # Only let 10 message in the chat history for context window efficiency
        memory = self._get_session_buffer_memory(session_id)
        self._logger.log_info(
            f"------------------- Conversation of User {session_id} -------------------\n"
            f"{memory.chat_memory.messages}\n"
            f"------------------- End of Conversation for User {session_id} -----------"
        )

        agent_executor = AgentExecutor(
            agent=self._agent,
            tools=tools,
            verbose=True,
            max_execution_time=60,
            max_iterations=15,
            memory=memory,
            allow_dangerous_code=True,
            handle_parsing_errors=True,
        )

        query = "info kost semanggi harga 1.5 dong"
        response = agent_executor.invoke({"input": query})
        print(response.get("output", "No output returned"))

        if task == RETRIEVE_BOARDING_HOUSES_OR_BUILDINGS:

            buildings_filter = BuildingsFilter(**result)
            self._logger.log_debug(f"[{session_id}]: Filters - {buildings_filter}")

            filter_array = self._prepare_filters(buildings_filter)

            building_instance = None
            with GeocodingAPI(self._logger) as obj:
                try:
                    query = (
                        buildings_filter.building_address
                        if buildings_filter.building_address
                        else buildings_filter.building_proximity
                    )
                    if query is not None:
                        result = self._chat_completion.execute(
                            {
                                "prompts": query,
                            },
                            self._location_verifier_prompt_parser,
                            [location_verifier_template],
                        ).get("address")

                        geo_query = query if result in [None, "None"] else result
                        self._logger.log_debug(
                            f"[{session_id}]: Verified address: {geo_query}"
                        )
                        geocode_data = obj.execute_geocode_by_address(geo_query)
                        if len(geocode_data) > 0:
                            self._logger.log_debug(
                                f"[{session_id}]: Got geocode data: {geocode_data}"
                            )
                            lat_long = geocode_data[0]["geometry"]["location"]
                            filter_array["building_geolocation"] = (
                                lambda distance: append_building_geolocation_filter(
                                    lat_long, distance
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
        :param facility_query: query by facility to retrieve vector data from weaviate.
        :param location_query: query by location to retrieve vector data from weaviate.
        """
        limit, offset, retries, max_retries = 5, 0, 0, 3
        start_time, building_list, seen_uuids = time.time(), [], set()
        geolocation_stages, geolocation_stage_index = [3000], 0

        with WeaviateAPI(self._logger) as weaviate_client:
            while retries < max_retries:
                connected, building_collection, building_chunk_collection = (
                    self._connect_to_collections(weaviate_client) or (None, None, None)
                )
                try:
                    while len(building_list) < limit:
                        filters, with_geofilter = None, self._geofilter_check(
                            geolocation_stages, geolocation_stage_index, filter_array
                        )

                        if with_geofilter:
                            filters = self._apply_geofilter_conditions(
                                filter_array,
                                distance=geolocation_stages[geolocation_stage_index],
                            )

                            self._logger.log_debug(
                                f'[{session_id}]: Executing facility query "{facility_query}"'
                            )
                            response = query_building(
                                building_collection,
                                facility_query,
                                filters,
                                limit,
                                offset,
                            )
                        else:
                            filters = self._apply_non_geofilter_conditions(filter_array)

                            self._logger.log_debug(
                                f'[{session_id}]: Executing location query "{location_query}"'
                            )
                            response = query_building_with_building_as_reference(
                                building_chunk_collection,
                                location_query,
                                filters,
                                limit,
                                offset,
                            )

                        if not response.objects:
                            if self._handle_empty_geosearch(
                                session_id,
                                with_geofilter,
                                geolocation_stages,
                                geolocation_stage_index,
                                facility_query,
                                location_query,
                            ):
                                geolocation_stage_index += 1
                                offset = 0
                            else:
                                break
                        else:
                            self._process_response(
                                session_id,
                                with_geofilter,
                                response,
                                building_list,
                                seen_uuids,
                                limit,
                            )
                            if len(building_list) >= limit:
                                break
                        offset += limit

                    self._log_query_execution_time(
                        session_id, start_time, building_list
                    )
                    break

                except Exception as e:
                    if retries >= max_retries:
                        self._logger.log_exception(
                            f"[{session_id}]: Weaviate query failed after {max_retries} retries. {e}"
                        )
                    else:
                        self._logger.log_warning(
                            f"[{session_id}]: Query attempt {retries} failed. Error: {e}"
                        )
                        retries += 1
                finally:
                    weaviate_client.close_connection_to_server(connected)

        return self.feedback_prompt(prompt, session_id, found=building_list or True)

    def feedback_prompt(self, prompt, session_id, reask=False, found=None) -> Message:
        """
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        :param session_id: session id of the chat.
        :param reask: reask flag.
        :param found: data found elements.
        """
        self._logger.log_info(
            f"[{session_id}]: Is reask for something is necessary: {reask}\n[{session_id}]: Is search found: {True if found else False}"
        )

        template = reask_template if reask else default_reply_template
        input_variables = [
            "prompts",
            "service_pic_number",
            "advertising_pic_number",
            "seen_buildings",
            "result",
        ]
        runnable_input = {
            "prompts": prompt,
            "service_pic_number": SERVICE_PIC_NUMBER,
            "advertising_pic_number": ADVERTISING_PIC_NUMBER,
            "seen_buildings": "\n".join(
                self._store[session_id]["session_buildings_seen"]
            ),
        }

        if found:
            template = building_found_template
            runnable_input["result"] = found

        output = self.respond(
            template, input_variables, runnable_input, session_id
        ).replace("**", "")
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
        template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate(
                    prompt=PromptTemplate(
                        template=seen_buildings_template,
                        input_variables=input_variables,
                    )
                ),
                SystemMessagePromptTemplate(
                    prompt=PromptTemplate(
                        template=template, input_variables=input_variables
                    )
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{prompts}"),
            ]
        )

        chain = template | self._client | StrOutputParser()
        with_message_history = RunnableWithMessageHistory(
            chain,
            self._get_session_message_history,
            input_messages_key="prompts",
            history_messages_key="history",
        )

        result: Runnable = with_message_history.invoke(
            runnable_input, config={"configurable": {"session_id": session_id}}
        )

        return result

    def _create_session_buffer_memory(
        self, session_id: str
    ) -> LimitedConversationBufferMemory:
        """Create session buffer memory
        :param session_id: chat session id
        :return: LimitedConversationBufferMemory
        """
        return LimitedConversationBufferMemory(
            memory_key=f"chat_history-{session_id}",
            return_messages=True,
            k=10,
        )

    def _get_session_buffer_memory(
        self, session_id: str
    ) -> LimitedConversationBufferMemory:
        """Get buffer memory by session id
        :param session_id: chat session id
        :return: LimitedConversationBufferMemory
        """
        if session_id not in self._store:
            self._store[session_id] = self._create_session_buffer_memory(session_id)
        return self._store[session_id]

    def _prepare_filters(self, buildings_filter: BuildingsFilter):
        filter_array = None
        filter_array = {
            "housing_price": lambda with_reference: append_housing_price_filters(
                buildings_filter, [], with_reference
            ),
            "building_facility": append_building_facility_filters(buildings_filter, []),
            "building_note": append_building_note_filters(buildings_filter, []),
        }

        return filter_array

    def _connect_to_collections(self, weaviate_client: WeaviateAPI):
        """Connect to the necessary collections for querying."""
        connected = weaviate_client.connect_to_server(int(USE_MODULE), MODULE_USED)
        if connected is None:
            raise RuntimeError(
                f"Runtime Error - 'connected' variable value is {connected}"
            )

        building_collection = connected.collections.get(BUILDINGS_COLLECTION_NAME)
        building_chunk_collection = connected.collections.get(
            BUILDING_CHUNKS_COLLECTION_NAME
        )
        return connected, building_collection, building_chunk_collection

    def _geofilter_check(
        self,
        geolocation_stages: list[int],
        geolocation_stage_index: int,
        filter_array: dict[str, list],
    ):
        """Check if geolocation filter can be applied."""
        return callable(
            filter_array.get("building_geolocation")
        ) and geolocation_stage_index < len(geolocation_stages)

    def _apply_geofilter_conditions(
        self, filter_array: dict[str, list], distance: float
    ):
        """Apply geolocation and housing price filters."""
        housing_price_filter = filter_array["housing_price"](False)
        filters = Filter.all_of(housing_price_filter) if housing_price_filter else None
        geofilter = filter_array["building_geolocation"](distance)
        return filters & geofilter if filters else geofilter

    def _apply_non_geofilter_conditions(self, filter_array: dict[str, list]):
        """Apply non-geolocation filters."""
        facility_filters = (
            Filter.any_of(filter_array["building_facility"])
            if filter_array["building_facility"]
            else None
        )
        note_filter = (
            Filter.any_of(filter_array["building_note"])
            if filter_array["building_note"]
            else None
        )

        housing_price_filter = filter_array["housing_price"](True)
        price_filters = (
            Filter.all_of(housing_price_filter) if housing_price_filter else None
        )
        filters = facility_filters & note_filter if facility_filters else note_filter
        filters = filters & price_filters if filters else price_filters
        return filters

    def _handle_empty_geosearch(
        self,
        session_id: str,
        with_geofilter: bool,
        geolocation_stages: list[int],
        geolocation_stage_index: int,
        facility_query: str,
        location_query: str,
    ):
        """Handle cases with no results."""
        if with_geofilter:
            self._logger.log_debug(
                f"[{session_id}]: No results at {geolocation_stages[geolocation_stage_index]} meters for query: {facility_query}"
            )
            return True
        self._logger.log_debug(
            f"[{session_id}]: No results for query: {location_query}"
        )
        return False

    def _process_response(
        self,
        session_id: str,
        with_geofilter: bool,
        response: QueryReturn[WeaviateProperties, CrossReferences],
        building_list: list,
        seen_uuids: set,
        limit: int,
    ):
        """Process each object in the response and add to building_list."""

        # clear the existing seen buildings set
        self._store[session_id]["session_buildings_seen"].clear()

        # loop through the response objects along with filtering which object should be appended
        for index, obj in enumerate(response.objects):
            if with_geofilter:
                self._add_building_instance(
                    session_id, index, obj, seen_uuids, building_list
                )
            else:
                for ref_obj in obj.references["hasBuilding"].objects:
                    if ref_obj.uuid not in seen_uuids:
                        self._add_building_instance(
                            session_id,
                            index,
                            ref_obj,
                            seen_uuids,
                            building_list,
                        )
            if len(building_list) >= limit:
                break

    def _add_building_instance(
        self,
        session_id: str,
        obj_index: int,
        obj: Object[WeaviateProperties, CrossReferences],
        seen_uuids: set,
        building_list: list,
    ):
        """Add a building instance to the list after checking for duplicates."""
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
            image_url=obj.properties["imageURL"],
        )
        formatted_info = building_object_template.format(
            number=obj_index + 1,
            title=building_instance.building_title,
            address=building_instance.building_address,
            facilities=building_instance.building_description,
            price=building_instance.housing_price,
            name=building_instance.owner_name,
            whatsapp=building_instance.owner_whatsapp,
            phonenumber=building_instance.owner_phone_number,
        )
        self._store[session_id]["session_buildings_seen"].add(formatted_info)
        building_list.append(building_instance)

    def _log_query_execution_time(
        self, session_id: str, start_time: float, building_list: list
    ):
        """Log the time taken for the query and total objects found."""
        elapsed_time = time.time() - start_time
        self._logger.log_info(
            f"[{session_id}]: Query completed in {elapsed_time:.2f} seconds. Total buildings found: {len(building_list)}"
        )
