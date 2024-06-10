import weaviate as weaviate_lib
from langchain_weaviate.vectorstores import WeaviateVectorStore
from src.interactor.interfaces.weaviate.api import WeaviateAPIInterface

class WeaviateAPI(WeaviateAPIInterface):
    """ WeaviateAPI class.
    """

    def __init__(self, docs, embeddings) -> None: 
        # connect Weaviate Cluster

        self._weaviate_client = weaviate_lib.connect_to_local()
        self._vectorstore = WeaviateVectorStore.from_documents(docs, embeddings, client=self._weaviate_client)