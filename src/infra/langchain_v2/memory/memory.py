from langchain.memory import ConversationBufferMemory


class LimitedConversationBufferMemory(ConversationBufferMemory):
    def __init__(self, k=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._k = k

    def save_context(self, inputs, outputs):
        super().save_context(inputs, outputs)
        # Limit messages to the last k exchanges
        self.chat_memory.messages = self.chat_memory.messages[-self._k :]
