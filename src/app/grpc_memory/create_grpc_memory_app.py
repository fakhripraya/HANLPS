""" Main GRPC In-Memory app
"""

import grpc
import sys
sys.path.append("./proto/messaging")
from configs.config import INSECURE_PORT
from proto.messaging import messaging_pb2_grpc as handler
from concurrent import futures
from src.app.grpc_memory.servicer.messaging_servicer import MessagingServicer
from src.interactor.interfaces.logger.logger import LoggerInterface

def create_grpc_memory_app(logger: LoggerInterface) -> None:
    """ Create Main GRPC In-Memory app
    """
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        handler.add_MessagingServicer_to_server(MessagingServicer(), server)
        server.add_insecure_port(INSECURE_PORT)
        
        server.start()
        logger.log_info("GRPC server started on port 50051")
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
        logger.log_info(f"Server has been stopped with keyboard interaction")
    except Exception as e:
        logger.log_exception(f"Failed to serve the app: {e}")
