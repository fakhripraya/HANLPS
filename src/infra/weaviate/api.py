import weaviate as weaviate_lib
from configs.config import OPENAI_API_KEY
from langchain_weaviate.vectorstores import WeaviateVectorStore
from src.interactor.interfaces.weaviate.api import WeaviateAPIInterface
import weaviate.classes as wvc

class WeaviateAPI(WeaviateAPIInterface):
    """ WeaviateAPI class.
    """

    def __init__(self, docs, embeddings) -> None: 
        # connect Weaviate Cluster
        
        headers = {
            "X-OpenAI-Api-Key": OPENAI_API_KEY
        } 

        self._weaviate_client = weaviate_lib.connect_to_local(headers=headers)
        # self._vectorstore = WeaviateVectorStore.from_documents(docs, embeddings, client=self._weaviate_client)
        try:
            print("something")
        finally:
            self._weaviate_client.close()
        