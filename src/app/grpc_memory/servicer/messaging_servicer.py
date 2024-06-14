from protofile import messaging_pb2_grpc, messaging_pb2 as messaging
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.langchain.api import LangchainAPI
from src.app.grpc_memory.controller.messaging_controller import MessagingController

class MessagingServicer(messaging_pb2_grpc.MessagingServiceServicer):

    def __init__(self, logger: LoggerInterface, llm: LangchainAPI):
        self.logger = logger
        self.llm = llm
        
    def textMessaging(self, request, context):
        controller = MessagingController(self.logger, self.llm)
        controller.get_message(request)
        result = controller.execute()
        end_result = result['content']
        return messaging.MessageResponse(result=end_result)