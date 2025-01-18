""" Module for LangchainAPIV2
"""

# Standard and third-party libraries
import time
import json
import traceback
from pydantic import ValidationError

# Source-specific imports
from src.domain.entities.message.message import Message
from src.domain.enum.tool_types.tool_types import ToolType
from src.domain.pydantic_models.agent_tool_output.agent_tool_output import (
    AgentToolOutput,
    BuildingsFilter
)
from src.infra.langchain_v2.agent.agent import create_agent
from src.infra.langchain_v2.tools.tools import BoardingHouseAgentTools
from src.infra.langchain_v2.memory.memory import LimitedConversationBufferMemory
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

        agent_tools = BoardingHouseAgentTools(self._logger, session_id)
        with self._create_agent_executor(session_id, agent_tools) as agent_executor:
            # We only let 10 messages in the chat history for context window efficiency
            self._logger.log_info(
                f"------------------- Conversation of User {session_id} -------------------\n"
                f"{agent_executor.memory.load_memory_variables({}).get('chat_history', [])}\n"
                f"------------------- End of Conversation for User {session_id} -----------"
            )

            output = agent_executor.invoke({"input": prompt}).get("output", None)
            if output is None:
                raise ValueError("Invalid agent response")
            

            formatted_output: AgentToolOutput | None
            try:
                formatted_json = json.load(output)
                formatted_output = AgentToolOutput.model_validate_json(formatted_json)
            except (json.JSONDecodeError, TypeError, ValidationError):
                formatted_output = AgentToolOutput(chat_output=str(output))

            return self._execute_agent_action(agent_tools, formatted_output, prompt)


    @contextmanager
    def _create_agent_executor(
        self, session_id: str, agent_tools: BoardingHouseAgentTools
    ):
        """
        Context manager for creating and managing the AgentExecutor.
        :param session_id: chat session id.
        :param agent_tools: the tools of the agent.
        """
        start_time = time.time()

        memory = self._get_session_buffer_memory(session_id)
        tools = [
            Tool(
                name="SearchPointOfInterest",
                func=agent_tools.analyze_nearby_poi_by_address_input,
                description="Search for nearby point of interest based on the specified address.",
            ),
            Tool(
                name="SearchSpecificLocation",
                func=agent_tools.analyze_specific_search_input,
                description="Search for specific given address location.",
            ),
            Tool(
                name="SaveLocation",
                func=agent_tools.analyze_save_location_input,
                description="Save the location data temporarily.",
            ),
            Tool(
                name="GetDirection",
                func=agent_tools.analyze_get_direction,
                description="Get the directional navigation start to end geocode data.",
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
    
    def _execute_agent_action(self, agent_tools: BoardingHouseAgentTools, formatted_output: AgentToolOutput, prompt: str):
        print(formatted_output)
        action_map = {
            ToolType.SEARCH_POINT_OF_INTEREST.value: lambda: agent_tools.search_nearby_poi_by_address(formatted_output.input_field), 
            ToolType.SEARCH_SPECIFIC_LOCATION.value: lambda: agent_tools.search_specific_by_address(formatted_output.input_field), 
            ToolType.SAVE_LOCATION.value: lambda: agent_tools.save_location(formatted_output.input_field), 
            ToolType.GET_DIRECTION.value: lambda: agent_tools.get_direction(formatted_output.input_field), 
        } 
        
        try:
            if formatted_output.input_code is None:
                return Message(input=prompt, output=formatted_output.chat_output)
            
            result = action_map[formatted_output.input_code]()
            print(result)
            if isinstance(result, Message):
                return result.input(prompt)
            else:
                raise ValueError("Invalid Message instance")
        except KeyError:
            raise ValueError("Invalid input code")
        except Exception as e:
            raise Exception(f"Error during agent action: {e}")
