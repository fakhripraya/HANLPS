from collections import deque
from langchain_community.chat_message_histories import ChatMessageHistory
from typing import Deque

class DequeChatMessageHistory(ChatMessageHistory):
    def __init__(self, maxlen: int = 100):
        super().__init__()
        # Initialize deque with a maximum length
        self.messages: Deque = deque(maxlen=maxlen)

    def add_message(self, message):
        """Add a message to the history."""
        self.messages.append(message)

    def get_messages(self):
        """Retrieve all messages in the history."""
        return list(self.messages)
