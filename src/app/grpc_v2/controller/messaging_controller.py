from enum import Enum
from src.app.grpc_v2.presenters.messaging_presenter import MessagingPresenter
from src.infra.langchain_v2.api import LangchainAPIV2
from src.infra.repositories.in_memory.messaging_in_memory_repository import (
    MessagingInMemoryRepository,
)
from src.interactor.dtos.messaging_dtos import MessagingInputDto
from src.interactor.usecases.messaging_usecase_v2 import MessagingUseCaseV2
from src.interactor.interfaces.logger.logger import LoggerInterface


class ActionType(Enum):
    SEND_MESSAGE = "send_message"
    CLEAR_HISTORY = "clear_history"


class MessagingController:
    def __init__(self, logger: LoggerInterface, langchain_api: LangchainAPIV2):
        self._logger = logger
        self._langchain_api = langchain_api

    def execute(self, grpc_message, action: ActionType) -> dict:
        """Delegates actions to their respective methods."""
        # Validate sessionId
        if not grpc_message.sessionId:
            raise ValueError("Session ID is required")

        # Route to the correct method based on action
        if action == ActionType.SEND_MESSAGE:
            return self._handle_send_message(grpc_message)
        elif action == ActionType.CLEAR_HISTORY:
            return self._handle_clear_history(grpc_message.sessionId)
        else:
            raise ValueError("Invalid action type")

    def _handle_send_message(self, grpc_message) -> dict:
        """Handles sending a message."""
        if not grpc_message.content:
            raise ValueError("Content is required for sending a message")

        input_dto = MessagingInputDto(grpc_message.sessionId, grpc_message.content)
        use_case = self._create_use_case()
        result = use_case.process_message(input_dto)
        return result

    def _handle_clear_history(self, session_id: str) -> dict:
        """Handles clearing message history."""
        use_case = self._create_use_case()
        use_case.clear_message_history(session_id)
        return

    def _create_use_case(self) -> MessagingUseCaseV2:
        """Creates and returns an instance of the MessagingUseCaseV2."""
        repository = MessagingInMemoryRepository()
        presenter = MessagingPresenter()
        return MessagingUseCaseV2(
            self._logger, presenter, repository, self._langchain_api
        )
