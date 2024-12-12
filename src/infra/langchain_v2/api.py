""" Module for LangchainAPIV2
"""

# Standard and third-party libraries
import traceback

# Source-specific imports
from src.domain.entities.message.message import Message
from src.infra.langchain_v2.agent.agent import create_agent
from src.infra.langchain_v2.tools.tools import BoardingHouseAgentTools
from src.infra.langchain_v2.memory.memory import LimitedConversationBufferMemory
from src.infra.langchain_v2.formatter.formatter import JSONFormatter
from src.interactor.interfaces.langchain_v2.api import LangchainAPIV2Interface
from src.interactor.interfaces.logger.logger import LoggerInterface
# Langchain and related libraries
from langchain.agents import AgentExecutor, Tool
from contextlib import contextmanager

class LangchainAPIV2(LangchainAPIV2Interface):
    """LangchainAPIV2 class."""

    def __init__(self, llm_type: str, logger: LoggerInterface) -> None:
        self._logger = logger
        self._store = {}
        self._agent = create_agent(llm_type, logger)
        self._formatter = JSONFormatter()

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

    def execute_search_agent(self, session_id, prompt) -> Message:
        """
        Execute search agent boarding house search
        :param session_id: chat session id.
        :param prompt: chat message to be analyzed.
        """
        self._logger.log_info(f"[{session_id}]: User prompt: {prompt}")

        # Only let 10 messages in the chat history for context window efficiency
        memory = self._get_session_buffer_memory(session_id)
        self._logger.log_info(
            f"------------------- Conversation of User {session_id} -------------------\n"
            f"{memory.chat_memory.messages}\n"
            f"------------------- End of Conversation for User {session_id} -----------"
        )

        with self._create_agent_executor(session_id) as agent_executor:
            response = agent_executor.invoke({"input": prompt})
            output = response.get("output", "No output returned")
            self._logger.log_info(f"[{session_id}]: {output}")

            return Message(input=prompt, output=output, output_content=None)

    @contextmanager
    def _create_agent_executor(self, session_id: str):
        """Context manager for creating and managing the AgentExecutor."""
        memory = self._get_session_buffer_memory(session_id)

        agent_tools = BoardingHouseAgentTools(self._logger, session_id, self._formatter)
        tools = [
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
        ]

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
        try:
            yield agent_executor
        finally:
            self._logger.log_info(f"AgentExecutor for session {session_id} cleaned up.")

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
