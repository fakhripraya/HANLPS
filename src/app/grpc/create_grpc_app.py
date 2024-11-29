""" Main GRPC In-Memory app
"""

import grpc
import sys
import traceback

sys.path.append("./protofile")
from configs.config import INSECURE_PORT, LLM_USED
from protofile.messaging.proto import messaging_pb2_grpc as handler
from concurrent import futures
from src.app.grpc.servicer.messaging_servicer import MessagingServicer
from src.domain.constants import OPENAI, HUGGING_FACE, GEMINI
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.langchain.api import LangchainAPI


class GRPCApp:
    def __init__(self, logger: LoggerInterface):
        try:
            self._logger = logger

            grpc_max_workers = 10
            self._logger.log_info(
                f"Creating GRPC server with {grpc_max_workers} workers"
            )
            self._grpc_server = grpc.server(
                futures.ThreadPoolExecutor(max_workers=grpc_max_workers)
            )

            with LangchainAPI(self.define_llm_type(), self._logger) as langchain_api:
                # register grpc handler
                handler.add_MessagingServiceServicer_to_server(
                    MessagingServicer(self._logger, langchain_api), self._grpc_server
                )

        except Exception as e:
            self._logger.log_critical(f"Error initializing App Instance: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._logger.log_error(f"[{exc_type}]: {exc_val}")
            self._logger.log_error(f"Traceback: {traceback.format_tb(exc_tb)}")
        self.stop_server()

    def define_llm_type(self):
        """define llm type"""
        if LLM_USED == str(OPENAI):
            return OPENAI
        elif LLM_USED == str(HUGGING_FACE):
            return HUGGING_FACE
        elif LLM_USED == str(GEMINI):
            return GEMINI
        else:
            raise ValueError("Invalid LLM type")

    def create_server(self):
        """Create the GRPC server and start it."""
        try:
            self._logger.log_info(f"Connecting GRPC app to port [::]:{INSECURE_PORT}")
            self._grpc_server.add_insecure_port(f"[::]:{INSECURE_PORT}")
            self._grpc_server.start()
            self._logger.log_info(f"GRPC server started on port [::]:{INSECURE_PORT}")

            self._grpc_server.wait_for_termination()
        except KeyboardInterrupt:
            self._logger.log_exception(
                "Server has been stopped with keyboard interaction"
            )
        except MemoryError as me:
            self._logger.log_critical(f"Ran out of memory: {me}")
        except grpc.RpcError as rpc_error:
            self._logger.log_critical(f"gRPC error occurred: {rpc_error}")
        except OSError as os_error:
            self._logger.log_critical(f"Operating system error: {os_error}")
        except RuntimeError as runtime_error:
            self._logger.log_critical(f"Runtime error occurred: {runtime_error}")
        except Exception as e:
            self._logger.log_critical(f"Failed to serve the app: {e}")

    def stop_server(self):
        """Stop the GRPC server."""
        if self._grpc_server:
            self._grpc_server.stop(0)
