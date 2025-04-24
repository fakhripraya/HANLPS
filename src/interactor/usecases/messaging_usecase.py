import json
from src.interactor.dtos.messaging_dtos import MessagingInputDto, MessagingOutputDto
from src.interactor.interfaces.presenters.message_presenter import (
    MessagingPresenterInterface,
)
from src.interactor.interfaces.repositories.in_memory.messaging_repository import (
    MessagingRepositoryInterface,
)
from src.interactor.validations.messaging_validator import MessagingInputDtoValidator
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.errors.error_classes import ItemNotCreatedException
from src.infra.langchain.api import LangchainAPI


class MessagingUseCase:
    """Handles messaging operations, including message processing and history clearing."""

    def __init__(
        self,
        logger: LoggerInterface,
        presenter: MessagingPresenterInterface,
        repository: MessagingRepositoryInterface,
        llm: LangchainAPI,
    ):
        self.logger = logger
        self.presenter = presenter
        self.repository = repository
        self.llm = llm

    def process_message(self, input_dto: MessagingInputDto) -> dict:
        """Processes a user message and returns the response."""
        # Validate the input
        validator = MessagingInputDtoValidator(input_dto.to_dict())
        validator.validate()

        # Use the LLM to analyze the prompt
        action_output, message_output = self.llm.analyze_prompt(input_dto.sessionId, input_dto.content)
        message = self.repository.create(
            input=message_output.input,
            output=message_output.output,
            output_content=message_output.output_content,
        )

        if message is None:
            self.logger.log_error("Message creation failed")
            raise ItemNotCreatedException(input_dto.content, "Message")

        # Convert building content to JSON (if applicable)
        buildings_dict = [
            building.to_dict() for building in (message_output.output_content or [])
        ]
        buildings_json = json.dumps(buildings_dict)

        # Prepare the output DTO and presenter response
        output_dto = MessagingOutputDto(
            input=message_output.input,
            output=message_output.output,
            output_content=buildings_json,
            action=action_output.action
        )

        return self.presenter.present(output_dto)

    def clear_message_history(self, session_id: str):
        """Clears the message history for a given session."""
        cleared = self.llm.clear_messaging_history(session_id)
        if cleared:
            self.logger.log_info(f"Message history cleared for session: {session_id}")
            return
        else:
            self.logger.log_error(f"Failed to clear history for session: {session_id}")
            raise ItemNotCreatedException(session_id, "ClearHistory")
