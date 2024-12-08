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
from src.infra.langchain_v2.tools.tools import BoardingHouseAgentTools
from src.infra.langchain_v2.memory.memory import LimitedConversationBufferMemory
from src.infra.geocoding.api import GeocodingAPI
from src.interactor.interfaces.langchain_v2.api import LangchainAPIV2Interface
from src.interactor.interfaces.logger.logger import LoggerInterface

# Langchain and related libraries
from langchain.agents import AgentExecutor, Tool
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts.chat import SystemMessagePromptTemplate
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
from src.infra.repositories.weaviate.filters.buildings.buildings import (
    append_housing_price_filters,
    append_building_facility_filters,
    append_building_note_filters,
    append_building_geolocation_filter,
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

        agent_tools = BoardingHouseAgentTools(self._logger)
        agent_executor = AgentExecutor(
            agent=self._agent,
            tools=[
                Tool(
                    name="SearchBoardingHouse",
                    func=agent_tools.search_boarding_house,
                    description="Search for boarding houses based on the specified criteria.",
                ),
                Tool(
                    name="SaveLocation",
                    func=agent_tools.save_location,
                    description="Save the location to the database.",
                ),
            ],
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
