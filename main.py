""" GRPC In-Memory Process Handler
"""

from src.app.grpc_memory.create_grpc_memory_app \
    import create_grpc_memory_app
from src.infra.logger.logger_default import LoggerDefault

logger = LoggerDefault()
if __name__ == "__main__":
    grpc_memory_app = create_grpc_memory_app(logger)
    