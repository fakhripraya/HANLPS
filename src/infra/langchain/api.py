import openai
from langchain_openai import OpenAIEmbeddings
from src.interactor.interfaces.langchain.api import LangchainAPIInterface
from src.infra.langchain.document_loader.document_loader import LangchainDocumentLoader
from src.infra.langchain.text_splitter.text_splitter import LangchainTextSplitter
from src.infra.vector_db.api import WeaviateAPI
from src.domain.constants import OPENAI, HUGGING_FACE

class LangchainAPI(LangchainAPIInterface, WeaviateAPI):
    """ LangchainAPI class.
    """

    def __init__(self, llm_type, api_key) -> None: 
        # TODO: Implement weaviate here
        if llm_type == OPENAI:
            self.create_open_ai_llm(api_key)
        elif llm_type == HUGGING_FACE:
            self.create_huggingface_llm(api_key)

    def create_open_ai_llm(self, api_key) -> None:
        """ 
        Create OpenAI LLM and register it as dependency
        :param api_key: the OpenAi api key
        """
        openai.api_key = api_key
        client = openai
        loader = LangchainDocumentLoader("pdf", 'pdfs', "**/*.pdf")
        data = loader.execute()

        text_splitter = LangchainTextSplitter(1000,0)
        docs = text_splitter.execute(data)
        
        embeddings = OpenAIEmbeddings(openai_api_key = api_key)
        
        self._client = client
        WeaviateAPI.__init__(self, docs, embeddings)

    def create_huggingface_llm(self, api_key) -> None:
        """ 
        Create Huggingface LLM and register it as dependency
        :param api_key: the Huggingface api key
        """
        openai.api_key = api_key
        client = openai
        loader = LangchainDocumentLoader("pdf", 'pdfs', "**/*.pdf")
        data = loader.execute()

        text_splitter = LangchainTextSplitter(1000,0)
        docs = text_splitter.execute(data)
        
        embeddings = OpenAIEmbeddings(openai_api_key = api_key)
        
        self._client = client
        WeaviateAPI.__init__(self, docs, embeddings)

    def receive_prompt(self, prompt) -> None:
        """ 
        Receive prompt, receive the prompt from the client app
        :param prompt: chat message to be analyzed.
        """

    def analyze_prompt(self, prompt) -> None:
        """ 
        Analyze prompt, define whether the prompt is a direct
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        """

    def feedback_prompt(self, prompt) -> None:
        """ 
        Feedback the prompt, process the prompt with the LLM
        :param prompt: chat message to be analyzed.
        """

    def respond(self, messages, client) -> None:
        """ 
        Respond the receiving prompt with the processed feedback
        command, a simple chat, etc.
        :param prompt: chat message to be analyzed.
        """
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=1,
        )
        return response.choices[0].message.content