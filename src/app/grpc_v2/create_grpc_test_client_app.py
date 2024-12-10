import unittest
from unittest.mock import MagicMock
import grpc
from concurrent import futures

# Import the necessary modules
from protofile.messaging.proto import messaging_pb2_grpc as handler
from protofile.messaging.proto.messaging_pb2 import MessageRequest, MessageResponse
from src.app.grpc.servicer.messaging_servicer import MessagingServicer
from src.domain.constants import OPENAI, HUGGING_FACE, GEMINI
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.langchain_v2.api import LangchainAPIV2


class MockLangchainAPIV2:
    """Mock implementation of LangchainAPIV2."""

    def __init__(self, llm_type, logger):
        self.llm_type = llm_type
        self.logger = logger

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockMessagingServicer(MessagingServicer):
    """Mock implementation of MessagingServicer for testing."""

    def textMessaging(self, request, context):
        return MessageResponse(result=f"Received: {request.content}")


class TestGRPCApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the gRPC test server."""
        cls.mock_logger = MagicMock(spec=LoggerInterface)
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

        # Replace LangchainAPIV2 with the mock
        cls.mock_langchain_api = MockLangchainAPIV2(OPENAI, cls.mock_logger)
        cls.servicer = MockMessagingServicer(cls.mock_logger, cls.mock_langchain_api)
        handler.add_MessagingServiceServicer_to_server(cls.servicer, cls.server)

        # Start the server on a test port
        cls.test_port = "[::]:50051"
        cls.server.add_insecure_port(cls.test_port)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        """Stop the gRPC test server."""
        cls.server.stop(0)

    def test_text_messaging(self):
        """Test the textMessaging gRPC endpoint."""
        with grpc.insecure_channel(self.test_port) as channel:
            stub = handler.MessagingStub(channel)

            # Simulate sending a message
            test_content = "Hello, this is a test!"
            response = stub.textMessaging(MessageRequest(content=test_content))

            # Assert the response
            self.assertEqual(response.result, f"Received: {test_content}")
            self.mock_logger.log_info.assert_called_with(
                f"Received request with content: {test_content}"
            )


if __name__ == "__main__":
    unittest.main()
