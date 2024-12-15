""" Module for LangchainAPIV2
"""

# Standard and third-party libraries
import time
import json
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
        self._llm_type = llm_type
        self._store = {}
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
        :return: bool
        """
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False

    def execute_search_agent(self, session_id, prompt) -> Message:
        """
        Execute search agent boarding house search
        :param session_id: chat session id.
        :param prompt: the search prompt.
        :return: Message
        """
        self._logger.log_info(f"[{session_id}]: User prompt: {prompt}")

        # Only let 10 messages in the chat history for context window efficiency
        memory = self._get_session_buffer_memory(session_id)
        self._logger.log_info(
            f"------------------- Conversation of User {session_id} -------------------\n"
            f"{memory.chat_memory.messages}\n"
            f"------------------- End of Conversation for User {session_id} -----------"
        )

        agent_tools = BoardingHouseAgentTools(self._logger, session_id, self._formatter)
        with self._create_agent_executor(session_id, agent_tools) as agent_executor:
            response = agent_executor.invoke({"input": prompt})
            output = response.get("output", None)

            if output is None:
                raise ValueError("Invalid agent response")

            formatted_output = json.loads(output)
            if formatted_output["input_code"] == "SEARCH_BUILDING":
                result = agent_tools.search_boarding_house(
                    formatted_output["input_field"]
                )

                return Message(input=prompt, output=output, output_content=None)
            elif formatted_output["input_code"] == "SAVE_BUILDING":
                result = agent_tools.save_boarding_house(
                    formatted_output["input_field"]
                )

                return Message(input=prompt, output="aaaa", output_content=None)

    @contextmanager
    def _create_agent_executor(
        self, session_id: str, agent_tools: BoardingHouseAgentTools
    ):
        """
        Context manager for creating and managing the AgentExecutor.
        :param session_id: chat session id.
        """
        start_time = time.time()

        memory = self._get_session_buffer_memory(session_id)
        tools = [
            Tool(
                name="SearchBoardingHouse",
                func=agent_tools.analyze_boarding_house_search_input,
                description="Search for boarding houses based on the specified criteria.",
            ),
            Tool(
                name="SaveLocation",
                func=agent_tools.analyze_boarding_house_save_input,
                description="Save the location to the database.",
            ),
        ]

        agent_executor = AgentExecutor(
            agent=create_agent(self._llm_type, tools, self._logger),
            tools=tools,
            verbose=True,
            max_execution_time=60,
            max_iterations=3,
            memory=memory,
            allow_dangerous_code=True,
            handle_parsing_errors=True,
            early_stopping_method="generate",
        )
        try:
            yield agent_executor
        except Exception as e:
            self._logger.log_exception(f"[{session_id}]: {e}")
        finally:
            self._log_agent_execution_time(session_id, start_time)

    def _create_buffer_memory(self) -> LimitedConversationBufferMemory:
        """Create session buffer memory
        :return: LimitedConversationBufferMemory
        """
        return LimitedConversationBufferMemory(
            memory_key="chat_history",
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
            self._store[session_id] = self._create_buffer_memory()
        return self._store[session_id]

    def _log_agent_execution_time(self, session_id: str, start_time: float):
        """Log the time taken for the query and total objects found."""
        elapsed_time = time.time() - start_time
        self._logger.log_info(
            f"[{session_id}]: Agent execution completed in {elapsed_time:.2f} seconds."
        )
