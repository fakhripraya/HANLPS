import grpc
import sys

sys.path.append("./protofile")
from configs.config import INSECURE_PORT
from protofile.messaging.proto import messaging_pb2_grpc, messaging_pb2 as messaging
from src.interactor.interfaces.logger.logger import LoggerInterface


def create_grpc_test_client_app(logger: LoggerInterface):
    """Create Main GRPC test client app"""
    with grpc.insecure_channel(INSECURE_PORT) as channel:
        stub = messaging_pb2_grpc.MessagingStub(channel)
        try:
            run_test(stub, logger)
        except Exception as e:
            logger.log_critical(f"Failed to serve the app: {e}")


def run_test(stub: messaging_pb2_grpc.MessagingStub, logger: LoggerInterface) -> None:
    # Get user Input
    chat_content = input("Please input the chat: ")
    response = stub.textMessaging(messaging.MessageRequest(content=chat_content))
    logger.log_info(f"Result: {response.result}")
