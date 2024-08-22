""" GRPC In-Memory Process Handler
"""

from src.app.grpc.create_grpc_app \
    import GRPCApp
from src.infra.logger.logger_default import LoggerDefault
from dotenv import load_dotenv

load_dotenv()
logger = LoggerDefault()
if __name__ == "__main__":
    app = GRPCApp(logger)
    app.create_server()
    