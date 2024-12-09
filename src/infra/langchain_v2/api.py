""" Module for LangchainAPIV2
"""

# Standard and third-party libraries
import time
import traceback

# Source-specific imports
from src.domain.entities.message.message import Message
from src.domain.prompt_templates import (
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

# Weaviate
from src.infra.repositories.weaviate.filters.buildings.buildings import (
    append_building_geolocation_filter,
)


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
        return Message(input=prompt, output="output", output_content=None)

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
