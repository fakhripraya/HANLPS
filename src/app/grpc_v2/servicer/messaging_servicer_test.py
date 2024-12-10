import unittest
from unittest.mock import MagicMock, patch
import grpc
from grpc import RpcContext
from protofile.messaging.proto import messaging_pb2 as messaging
from src.app.grpc.controller.messaging_controller import ActionType


class MockRpcContext(RpcContext):
    """Mock implementation of gRPC RpcContext for testing message servicer."""

    def __init__(self):
        self.code = None
        self.details = None

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details


class TestMessagingServicer(unittest.TestCase):

    def setUp(self):
        # Create mock logger and LangchainAPI
        self.mock_logger = MagicMock()
        self.mock_langchain_api = MagicMock()

        # Initialize the MessagingServicer with mocks
        from src.app.grpc.servicer.messaging_servicer import MessagingServicer

        self.servicer = MessagingServicer(self.mock_logger, self.mock_langchain_api)

    @patch("src.app.grpc.controller.messaging_controller.MessagingController")
    def test_textMessaging_success(self, MockMessagingController):
        # Mock the controller behavior
        mock_controller = MockMessagingController.return_value
        mock_controller.execute.return_value = {
            "input": "Hello",
            "output": "Hi there!",
            "output_content": ["Response content"],
        }

        # Prepare the request and context
        request = messaging.MessageRequest(sessionId="test-session", content="Hello")
        context = MockRpcContext()

        # Call the method
        response = self.servicer.textMessaging(request, context)

        # Assertions
        self.assertEqual(response.input, "Hello")
        self.assertEqual(response.output, "Hi there!")
        self.assertEqual(response.output_content, ["Response content"])
        self.mock_logger.log_info.assert_called_with(
            "Result generated for session test-session"
        )

    @patch("src.app.grpc.controller.messaging_controller.MessagingController")
    def test_textMessaging_exception(self, MockMessagingController):
        # Mock the controller to raise an exception
        mock_controller = MockMessagingController.return_value
        mock_controller.execute.side_effect = Exception("Test exception")

        # Prepare the request and context
        request = messaging.MessageRequest(sessionId="test-session", content="Hello")
        context = MockRpcContext()

        # Call the method
        response = self.servicer.textMessaging(request, context)

        # Assertions
        self.assertIsInstance(response, messaging.MessageResponse)
        self.assertIsNone(response.input)
        self.assertIsNone(response.output)
        self.assertIsNone(response.output_content)
        self.assertEqual(context.code, grpc.StatusCode.INTERNAL)
        self.assertEqual(context.details, "Internal error: Test exception")
        self.mock_logger.log_exception.assert_called_with(
            "Exception in textMessaging: Test exception"
        )

    @patch("src.app.grpc.controller.messaging_controller.MessagingController")
    def test_clearMessageHistory_success(self, MockMessagingController):
        # Mock the controller behavior
        mock_controller = MockMessagingController.return_value

        # Prepare the request and context
        request = messaging.ClearMessageHistoryRequest(sessionId="test-session")
        context = MockRpcContext()

        # Call the method
        response = self.servicer.clearMessageHistory(request, context)

        # Assertions
        self.assertIsInstance(response, messaging.Empty)
        mock_controller.execute.assert_called_once_with(
            request, ActionType.CLEAR_HISTORY
        )

    @patch("src.app.grpc.controller.messaging_controller.MessagingController")
    def test_clearMessageHistory_exception(self, MockMessagingController):
        # Mock the controller to raise an exception
        mock_controller = MockMessagingController.return_value
        mock_controller.execute.side_effect = Exception("Test exception")

        # Prepare the request and context
        request = messaging.ClearMessageHistoryRequest(sessionId="test-session")
        context = MockRpcContext()

        # Call the method
        response = self.servicer.clearMessageHistory(request, context)

        # Assertions
        self.assertIsInstance(response, messaging.Empty)
        self.assertEqual(context.code, grpc.StatusCode.INTERNAL)
        self.assertEqual(context.details, "Internal error: Test exception")
        self.mock_logger.log_exception.assert_called_with(
            "Exception in clearMessageHistory: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
