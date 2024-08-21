""" GRPC Test Client App
"""

from src.app.grpc.create_grpc_test_client_app \
    import create_grpc_test_client_app
from src.infra.logger.logger_default import LoggerDefault
from dotenv import load_dotenv

load_dotenv()
logger = LoggerDefault()
if __name__ == '__main__':
   create_grpc_test_client_app(LoggerDefault)