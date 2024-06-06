""" Main GRPC In-Memory app
"""

import grpc
import sys
sys.path.append("./proto/messaging")
from proto.messaging import messaging_pb2_grpc
from concurrent import futures
from src.app.grpc_memory.servicer.messaging_servicer import MessagingServicer
from src.interactor.interfaces.logger.logger import LoggerInterface

def create_grpc_memory_app(logger: LoggerInterface) -> None:
    """ Create Main GRPC In-Memory app
    """
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        messaging_pb2_grpc.add_MessagingServicer_to_server(MessagingServicer(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        logger.log_info("GRPC server started on port 50051")
        server.wait_for_termination()
    except Exception as e:
        logger.log_exception(f"Failed to serve the app: {e}")
