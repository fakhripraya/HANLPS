# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import pytest
from src.interactor.usecases import messaging_usecase
from src.domain.entities.message import Message
from src.interactor.dtos.messaging_dtos \
    import MessagingInputDto, MessagingOutputDto
from src.interactor.interfaces.presenters.message_presenter \
    import MessagingPresenterInterface
from src.interactor.interfaces.repositories.messaging_repository \
    import MessagingRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.errors.error_classes import ItemNotCreatedException

def test_messaging_usecase(mocker, fixture_messaging_developer):
    message = Message(
        message_id=fixture_messaging_developer["message_id"],
        content=fixture_messaging_developer["content"],
    )
    presenter_mock = mocker.patch.object(
        MessagingPresenterInterface,
        "present"
    )
    repository_mock = mocker.patch.object(
        MessagingRepositoryInterface,
        "create"
    )

    input_dto_validator_mock = mocker.patch(
        "src.interactor.usecases.messaging_usecase.\
MessagingInputDtoValidator"
    )
    logger_mock = mocker.patch.object(
        LoggerInterface,
        "log_info"
    )
    repository_mock.create.return_value = message
    presenter_mock.present.return_value = "Test output"
    use_case = messaging_usecase.MessagingUseCase(
        presenter_mock,
        repository_mock,
        logger_mock
    )
    input_dto = MessagingInputDto(
        content=fixture_messaging_developer["content"],
    )
    result = use_case.execute(input_dto)
    repository_mock.create.assert_called_once()
    input_dto_validator_mock.assert_called_once_with(input_dto.to_dict())
    input_dto_validator_instance = input_dto_validator_mock.return_value
    input_dto_validator_instance.validate.assert_called_once_with()
    logger_mock.log_info.assert_called_once_with(
        "Message created successfully")
    output_dto = MessagingOutputDto(message)
    presenter_mock.present.assert_called_once_with(output_dto)
    assert result == "Test output"

    # Testing None return value from repository
    repository_mock.create.return_value = None
    message_content = fixture_messaging_developer["content"]
    with pytest.raises(ItemNotCreatedException) as exception_info:
        use_case.execute(input_dto)
    assert str(exception_info.value) == \
        f"Message '{message_content}' was not created correctly"

def test_messaging_usecase_empty_field(mocker, fixture_messaging_developer):
    presenter_mock = mocker.patch.object(
        MessagingPresenterInterface,
        "present"
    )
    repository_mock = mocker.patch.object(
        MessagingRepositoryInterface,
        "create"
    )
    logger_mock = mocker.patch.object(
        LoggerInterface,
        "log_info"
    )
    use_case = messaging_usecase.CreateProfessionUseCase(
        presenter_mock,
        repository_mock,
        logger_mock
    )
    input_dto = MessagingInputDto(
        content="",
    )
    with pytest.raises(ValueError) as exception_info:
        use_case.execute(input_dto)
    assert str(exception_info.value) == "Content: empty values not allowed"

    repository_mock.create.assert_not_called()
    presenter_mock.present.assert_not_called()
