"""Create Messaging Controller Module"""

from src.interactor.usecases.messaging_usecase import MessagingUseCase
from src.infra.repositories.in_memory.messaging_in_memory_repository import (
    MessagingInMemoryRepository,
)
from src.interactor.dtos.messaging_dtos import MessagingInputDto
from src.interactor.interfaces.controller.messaging_controller_interface import (
    MessagingControllerInterface,
)
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.app.grpc.presenters.messaging_presenter import MessagingPresenter
from src.infra.langchain.api import LangchainAPI


class MessagingController(MessagingControllerInterface):
    """Create Messaging Controller Class"""

    def __init__(self, logger: LoggerInterface, langchain_api: LangchainAPI):
        self._logger = logger
        self._langchain_api = langchain_api
        self._input_dto: MessagingInputDto

    def get_message(self, grpc_message) -> None:
        """Get Message packet from the GRPC Client
        :param json_input: Input data
        :raises: ValueError if message content are missing.
        """
        if grpc_message.content is not None:
            sessionId = str(grpc_message.sessionId)
            content = str(grpc_message.content)
            self._input_dto = MessagingInputDto(sessionId, content)
        else:
            raise ValueError("Missing message content")

    def execute(self) -> dict:
        """Executes the controller
        :returns: Message processed and send responses
        """
        repository = MessagingInMemoryRepository()
        presenter = MessagingPresenter()
        use_case = MessagingUseCase(self._logger, presenter, repository, self._langchain_api)
        result = use_case.execute(self._input_dto)
        return result
