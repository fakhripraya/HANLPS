""" GRPC In-Memory Process Handler
"""

from src.app.grpc_memory.create_grpc_memory_app \
    import GRPCMemoryApp
from src.infra.logger.logger_default import LoggerDefault
from dotenv import load_dotenv

load_dotenv()
logger = LoggerDefault()
if __name__ == "__main__":
    app = GRPCMemoryApp(logger)
    app.create_server()
    