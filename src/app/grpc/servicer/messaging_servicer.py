from protofile.messaging.proto import messaging_pb2_grpc, messaging_pb2 as messaging
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.langchain.api import LangchainAPI
from src.app.grpc.controller.messaging_controller import MessagingController


class MessagingServicer(messaging_pb2_grpc.MessagingServiceServicer):

    def __init__(self, logger: LoggerInterface, langchain_api: LangchainAPI):
        self._logger = logger
        self._langchain_api = langchain_api

    def textMessaging(self, request, context):
        try:
            controller = MessagingController(self._logger, self._langchain_api)
            controller.get_message(request)
            result = controller.execute()

            self._logger.log_info("Result Generated")
            return messaging.MessageResponse(
                input=result["input"],
                output=result["output"],
                output_content=result["output_content"],
            )
        except Exception as e:
            self._logger.log_exception(f"Exception: {e}")
