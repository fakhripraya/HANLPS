import grpc
from protofile.messaging.proto import messaging_pb2_grpc, messaging_pb2 as messaging

from src.app.grpc_v2.controller.messaging_controller import (
    MessagingController,
    ActionType,
)
from src.infra.langchain_v2.api import LangchainAPIV2
from src.interactor.interfaces.logger.logger import LoggerInterface


class MessagingServicer(messaging_pb2_grpc.MessagingServiceServicer):

    def __init__(self, logger: LoggerInterface, langchain_api: LangchainAPIV2):
        self._logger = logger
        self._langchain_api = langchain_api

    def textMessaging(self, request, context):
        try:
            controller = MessagingController(self._logger, self._langchain_api)
            result = controller.execute(request, ActionType.SEND_MESSAGE)
            self._logger.log_info(f"Result generated for session {request.sessionId}")

            return messaging.MessageResponse(
                input=result["input"],
                output=result["output"],
                output_content=result["output_content"],
            )
        except Exception as e:
            self._logger.log_exception(f"Exception in textMessaging: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {e}")
            return messaging.MessageResponse()  # Return empty response on error

    def clearMessageHistory(self, request, context):
        try:
            controller = MessagingController(self._logger, self._langchain_api)
            controller.execute(request, ActionType.CLEAR_HISTORY)
            return messaging.Empty()
        except Exception as e:
            self._logger.log_exception(f"Exception in clearMessageHistory: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {e}")
            return messaging.Empty()
