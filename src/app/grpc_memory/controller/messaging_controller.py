"""Create Messaging Controller Module"""

from src.interactor.usecases.messaging_usecase import MessagingUseCase
from src.infra.repositories.messaging_in_memory_repository \
    import MessagingInMemoryRepository
from src.interactor.dtos.messaging_dtos import MessagingInputDto
from src.interactor.interfaces.controller.messaging_controller_interface \
    import MessagingControllerInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.app.grpc_memory.presenters.messaging_presenter import \
    MessagingPresenter
from src.infra.langchain.api import LangchainAPI

class MessagingController(MessagingControllerInterface):
    """ Create Messaging Controller Class
    """
    def __init__(self, logger: LoggerInterface, llm: LangchainAPI):
        self.logger = logger
        self.llm = llm
        self.input_dto: MessagingInputDto

    def get_message(self, grpc_message) -> None:
        """ Get Message packet from the GRPC Client
        :param json_input: Input data
        :raises: ValueError if message content are missing.
        """
        if grpc_message.content is not None:
             sessionId = str(grpc_message.sessionId)
             content = str(grpc_message.content)
             self.input_dto = MessagingInputDto(sessionId, content)
        else:
            raise ValueError("Missing message content")
       
    def execute(self) -> dict:
        """ Executes the controller
        :returns: Message processed and send responses
        """
        repository = MessagingInMemoryRepository()
        presenter = MessagingPresenter()
        use_case = MessagingUseCase(self.logger, presenter, repository, self.llm)
        result = use_case.execute(self.input_dto)
        return result
