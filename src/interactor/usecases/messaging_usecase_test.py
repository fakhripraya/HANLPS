# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import pytest
from infra.langchain.api import LangchainAPI
from src.interactor.usecases import messaging_usecase
from src.domain.entities.message.message import Message
from src.interactor.dtos.messaging_dtos import MessagingInputDto, MessagingOutputDto
from src.interactor.interfaces.presenters.message_presenter import (
    MessagingPresenterInterface,
)
from src.interactor.interfaces.repositories.in_memory.messaging_repository import (
    MessagingRepositoryInterface,
)
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.errors.error_classes import ItemNotCreatedException


def test_messaging_usecase_send_message(mocker, fixture_messaging_developer):
    # Arrange
    message = Message(
        message_id=fixture_messaging_developer["message_id"],
        content=fixture_messaging_developer["content"],
    )
    presenter_mock = mocker.patch.object(MessagingPresenterInterface, "present")
    repository_mock = mocker.patch.object(MessagingRepositoryInterface, "create")
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    langchain_api_mock = mocker.patch.object(LangchainAPI, "analyze_prompt")

    repository_mock.create.return_value = message
    presenter_mock.present.return_value = "Test output"
    langchain_api_mock.return_value = {
        "input": fixture_messaging_developer["content"],
        "output": "Processed output",
        "output_content": [],
    }

    # Create the UseCase
    use_case = messaging_usecase.MessagingUseCase(
        logger_mock, presenter_mock, repository_mock, langchain_api_mock
    )

    # Create the input DTO
    input_dto = MessagingInputDto(
        sessionId=fixture_messaging_developer["session_id"],
        content=fixture_messaging_developer["content"],
    )

    # Act
    result = use_case.process_message(input_dto)

    # Assert
    repository_mock.create.assert_called_once()
    langchain_api_mock.assert_called_once_with(
        fixture_messaging_developer["session_id"],
        fixture_messaging_developer["content"],
    )
    logger_mock.log_info.assert_called_once_with("Message created successfully")
    output_dto = MessagingOutputDto(
        input="Processed input",
        output="Processed output",
        output_content="[]",  # Empty list for this test case
    )
    presenter_mock.present.assert_called_once_with(output_dto)
    assert result == "Test output"

    # Testing None return value from repository
    repository_mock.create.return_value = None
    message_content = fixture_messaging_developer["content"]
    with pytest.raises(ItemNotCreatedException) as exception_info:
        use_case.process_message(input_dto)
    assert (
        str(exception_info.value)
        == f"Message '{message_content}' was not created correctly"
    )


def test_messaging_usecase_clear_history(mocker, fixture_messaging_developer):
    # Arrange
    session_id = fixture_messaging_developer["session_id"]
    repository_mock = mocker.patch.object(MessagingRepositoryInterface, "clear_history")
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    langchain_api_mock = mocker.patch.object(LangchainAPI, "analyze_prompt")

    repository_mock.clear_history.return_value = True
    use_case = messaging_usecase.MessagingUseCase(
        logger_mock, mocker.Mock(), repository_mock, langchain_api_mock
    )

    # Act
    result = use_case.clear_history(session_id)

    # Assert
    repository_mock.clear_history.assert_called_once_with(session_id)
    logger_mock.log_info.assert_called_once_with(
        f"Message history cleared for session: {session_id}"
    )
    assert result == {"status": "History Cleared"}

    # Testing failure scenario (when repository fails to clear history)
    repository_mock.clear_history.return_value = False
    with pytest.raises(ItemNotCreatedException) as exception_info:
        use_case.clear_history(session_id)
    assert (
        str(exception_info.value)
        == f"Failed to clear history for session: {session_id}"
    )
