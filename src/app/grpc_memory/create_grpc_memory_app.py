""" Main GRPC In-Memory app
"""

import grpc
import sys
sys.path.append("./protofile")
from configs.config import INSECURE_PORT, OPENAI_API_KEY, LLM_USED
from protofile.messaging.proto import messaging_pb2_grpc as handler
from concurrent import futures
from src.app.grpc_memory.servicer.messaging_servicer import MessagingServicer
from src.domain.constants import OPENAI, HUGGING_FACE, GEMINI
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.langchain.api import LangchainAPI

class GRPCMemoryApp:
    def __init__(self, logger: LoggerInterface):
        self.logger = logger
        self.llm = LangchainAPI(self.define_llm_type(), OPENAI_API_KEY, self.logger)
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        # register grpc handler
        handler.add_MessagingServiceServicer_to_server(MessagingServicer(self.logger, self.llm), self.grpc_server)

    def define_llm_type(self):
        """define llm type"""
        if(LLM_USED == str(OPENAI)):
            return OPENAI
        elif(LLM_USED == str(HUGGING_FACE)):
            return HUGGING_FACE
        elif(LLM_USED == str(GEMINI)):
            return GEMINI
        else:
            raise Exception("Invalid LLM type")

    def create_server(self):
        """Create the GRPC server and start it."""
        try:
            self.grpc_server.add_insecure_port(INSECURE_PORT)
            self.grpc_server.start()
            self.logger.log_info(f"GRPC server started on port {INSECURE_PORT}")

            self.grpc_server.wait_for_termination()
        except KeyboardInterrupt:
            self.logger.log_info("Server has been stopped with keyboard interaction")
        except Exception as e:
            self.logger.log_exception(f"Failed to serve the app: {e}")
        finally:
            self.stop_server()

    def stop_server(self):
        """Stop the GRPC server."""
        if self.llm._weaviate_client and self.llm._weaviate_client.is_live:
            self.llm._weaviate_client.close()
        if self.grpc_server:
            self.grpc_server.stop(0)
        
