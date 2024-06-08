import grpc
import sys
sys.path.append("./proto/messaging")
from configs.config import INSECURE_PORT
from proto.messaging import messaging_pb2_grpc, messaging_pb2 as messaging
from src.interactor.interfaces.logger.logger import LoggerInterface

def create_grpc_memory_test_client_app(logger: LoggerInterface):
    """ Create Main GRPC test client app
    """
    with grpc.insecure_channel(INSECURE_PORT) as channel:
        stub = messaging_pb2_grpc.MessagingStub(channel)
        try:
            run_test(stub)
        except Exception as e:
            logger.log_exception(f"Failed to serve the app: {e}")

def run_test(stub:messaging_pb2_grpc.MessagingStub) -> None:
    # Get user Input 
    chat_content = input("Please input the chat: ")
    response = stub.textMessaging(messaging.MessageRequest(content=chat_content))
    print(f"Result: {response.result}")
    
