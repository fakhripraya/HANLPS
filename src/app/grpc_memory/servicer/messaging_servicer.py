from proto import messaging_pb2_grpc, messaging_pb2 as messaging
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.app.grpc_memory.controller.messaging_controller import MessagingController

class MessagingServicer(messaging_pb2_grpc.MessagingServiceServicer):

    def __init__(self, logger: LoggerInterface):
        self.logger = logger
        
    def textMessaging(self, request, context):
        # TODO: CONTROLLERNYA BLM BENER, BENERIN 
        # controller = MessagingController(self.logger)
        # controller.get_message(request)
        # result = controller.execute()
        end_result = "Received: " + request.content
        return messaging.MessageResponse(result=end_result)