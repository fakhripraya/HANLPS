import weaviate
from langchain.vectorstores import Weaviate
from src.interactor.interfaces.weaviate.api import WeaviateAPIInterface

class WeaviateAPI(WeaviateAPIInterface):
    """ WeaviateAPI class.
    """

    def __init__(self, cluster_url, api_key, llm_header, llm_key) -> None: 
        # connect Weaviate Cluster
        auth_config = weaviate.AuthApiKey(api_key=api_key)

        WEAVIATE_URL = cluster_url
        client = weaviate.Client(
            url=WEAVIATE_URL,
            additional_headers={llm_header and "X-OpenAI-Api-Key": llm_key},
            auth_client_secret=auth_config,
            startup_period=10
        )

        self._client = client