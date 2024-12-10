""" GRPC In-Memory Process Handler
"""

from src.app.grpc_v2.create_grpc_app import GRPCAppV2
from src.infra.logger.logger_default import LoggerDefault
from dotenv import load_dotenv

load_dotenv()
logger = LoggerDefault()
if __name__ == "__main__":
    app = GRPCAppV2(logger)
    app.create_server()
