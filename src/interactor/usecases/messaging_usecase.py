""" This module is responsible for messaging usecase.
"""

from typing import Dict
from src.interactor.dtos.messaging_dtos \
    import MessagingInputDto, MessagingOutputDto
from src.interactor.interfaces.presenters.message_presenter \
    import MessagingPresenterInterface
from src.interactor.interfaces.repositories.messaging_repository \
    import MessagingRepositoryInterface
from src.interactor.validations.messaging_validator \
    import MessagingInputDtoValidator
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.errors.error_classes import ItemNotCreatedException
from src.infra.langchain.api import LangchainAPI

class MessagingUseCase():
    """ This class is responsible for everything needed to do the messaging flow
    """

    def __init__(
            self,
            logger: LoggerInterface,
            presenter: MessagingPresenterInterface,
            repository: MessagingRepositoryInterface,
            llm: LangchainAPI
    ):
        self.logger = logger
        self.presenter = presenter
        self.repository = repository
        self.llm = llm

    def execute(
            self,
            input_dto: MessagingInputDto
    ) -> Dict:
        """ This method is responsible for messaging.
        :param input_dto: The input data transfer object.
        :type input_dto: MessagingInputDto
        :return: Dict
        """

        validator = MessagingInputDtoValidator(input_dto.to_dict())
        try:
            validator.validate()
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            raise

        #TODO: langchain logic here
        output = self.llm.receive_prompt(input_dto.content)

        #TODO: Store chat here
        message = self.repository.create(
            output,
        )
        if message is None:
            self.logger.log_exception("Message creation failed")
            raise ItemNotCreatedException(input_dto.content, "Message")
        
        output_dto = MessagingOutputDto(message)
        presenter_response = self.presenter.present(output_dto)
        return presenter_response
