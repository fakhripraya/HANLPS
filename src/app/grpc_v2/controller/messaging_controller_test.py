import pytest
from unittest.mock import MagicMock, patch
from src.app.grpc.controller.messaging_controller import MessagingController, ActionType
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.langchain_v2.api import LangchainAPIV2


# Fixture to provide sample messaging data
@pytest.fixture
def fixture_messaging_data():
    return {
        "sessionId": "test-session-123",
        "content": "Hello, this is a test message.",
    }


# Test for sending messages
def test_send_message(fixture_messaging_data):
    logger_mock = MagicMock(LoggerInterface)
    langchain_api_mock = MagicMock(LangchainAPIV2)

    # Patch use case, repository, and presenter
    with patch(
        "src.app.grpc.controller.messaging_controller.MessagingUseCase"
    ) as MockUseCase, patch(
        "src.app.grpc.controller.messaging_controller.MessagingInMemoryRepository"
    ) as MockRepository, patch(
        "src.app.grpc.controller.messaging_controller.MessagingPresenter"
    ) as MockPresenter:

        # Set up the use case mock
        mock_use_case_instance = MockUseCase.return_value
        mock_use_case_instance.execute.return_value = {
            "input": fixture_messaging_data["content"],
            "output": "Test Response",
            "output_content": "Processed Message",
        }

        # Initialize the controller
        controller = MessagingController(logger_mock, langchain_api_mock)

        # Execute the controller with the send action
        result = controller.execute(fixture_messaging_data, ActionType.SEND_MESSAGE)

        # Assertions
        assert result["input"] == fixture_messaging_data["content"]
        assert result["output"] == "Test Response"
        assert result["output_content"] == "Processed Message"
        MockUseCase.assert_called_once()
        MockRepository.assert_called_once()
        MockPresenter.assert_called_once()


# Test for clearing message history
def test_clear_message_history(fixture_messaging_data):
    logger_mock = MagicMock(LoggerInterface)
    langchain_api_mock = MagicMock(LangchainAPIV2)

    with patch(
        "src.app.grpc.controller.messaging_controller.MessagingUseCase"
    ) as MockUseCase, patch(
        "src.app.grpc.controller.messaging_controller.MessagingInMemoryRepository"
    ) as MockRepository, patch(
        "src.app.grpc.controller.messaging_controller.MessagingPresenter"
    ) as MockPresenter:

        # Set up the use case mock for clearing history
        mock_use_case_instance = MockUseCase.return_value
        mock_use_case_instance.execute.return_value = {"status": "History Cleared"}

        # Initialize the controller
        controller = MessagingController(logger_mock, langchain_api_mock)

        # Execute the controller with the clear history action
        result = controller.execute(fixture_messaging_data, ActionType.CLEAR_HISTORY)

        # Assertions
        assert result["status"] == "History Cleared"
        MockUseCase.assert_called_once()
        MockRepository.assert_called_once()
        MockPresenter.assert_called_once()


# Test for missing content in message
def test_missing_message_content():
    logger_mock = MagicMock(LoggerInterface)
    langchain_api_mock = MagicMock(LangchainAPIV2)

    controller = MessagingController(logger_mock, langchain_api_mock)

    # Missing content
    incomplete_data = {"sessionId": "test-session-123"}

    with pytest.raises(ValueError) as exception_info:
        controller.execute(incomplete_data, ActionType.SEND_MESSAGE)

    assert str(exception_info.value) == "Missing message content"
