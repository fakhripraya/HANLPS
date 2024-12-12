""" GRPC Test Client V2 App
"""

import unittest
from unittest.mock import MagicMock, patch


class TestGRPCInMemoryProcessHandler(unittest.TestCase):

    @patch("src.app.grpc.create_grpc_app.GRPCApp")
    @patch("src.infra.logger.logger_default.LoggerDefault")
    def test_grpc_in_memory_process_handler(self, MockLoggerDefault, MockGRPCApp):
        # Mock logger and GRPC app initialization
        mock_logger = MockLoggerDefault.return_value
        mock_grpc_app = MockGRPCApp.return_value

        # Simulate the GRPC app's `create_server` method
        mock_grpc_app.create_server = MagicMock()

        # Import the script to run the main block
        with patch("src.app.grpc.process_handler.__name__", "__main__"):
            from src.app.grpc import (
                process_handler,
            )  # Import within the patch context

            process_handler

        # Assertions
        MockLoggerDefault.assert_called_once()
        MockGRPCApp.assert_called_once_with(mock_logger)
        mock_grpc_app.create_server.assert_called_once()


if __name__ == "__main__":
    unittest.main()
