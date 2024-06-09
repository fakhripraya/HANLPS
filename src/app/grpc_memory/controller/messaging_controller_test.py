# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import pytest
from src.app.grpc_memory.controller.messaging_controller \
    import MessagingController
from src.interactor.dtos.messaging_dtos import MessagingInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface

def test_messaging(monkeypatch, mocker, fixture_messaging_developer):
    content = fixture_messaging_developer["content"]
    fake_user_inputs = {
        "content": content,
    }
    monkeypatch.setattr('builtins.input', lambda _: next(fake_user_inputs))

    mock_repository = mocker.patch(
        'src.app.grpc_memory.controller.messaging_controller.\
MessagingInMemoryRepository')
    mock_presenter = mocker.patch(
        'src.app.grpc_memory.controller.messaging_controller.\
MessagingPresenter')
    mock_use_case = mocker.patch(
        'src.app.grpc_memory.controller.messaging_controller.\
MessagingUseCase')
    mock_use_case_instance = mock_use_case.return_value
    logger_mock = mocker.patch.object(
        LoggerInterface,
        "log_info"
    )
    result_use_case = {
        "message_id": fixture_messaging_developer["message_id"],
        "content": fixture_messaging_developer["content"],
    }
    mock_use_case_instance.execute.return_value = result_use_case

    controller = MessagingController(logger_mock)
    controller.get_message(fake_user_inputs)
    result = controller.execute()

    mock_repository.assert_called_once_with()
    mock_presenter.assert_called_once_with()
    mock_use_case.assert_called_once_with(
        mock_presenter.return_value,
        mock_repository.return_value,
        logger_mock
    )
    input_dto = MessagingInputDto(content)
    mock_use_case_instance.execute.assert_called_once_with(input_dto)
    assert result["content"] == content

    # Test for missing inputs (name)
    fake_user_inputs = {
        "conten": content,
    }
    with pytest.raises(ValueError) as exception_info:
        controller.get_message(fake_user_inputs)
    assert str(exception_info.value) == "Missing Profession Name"
