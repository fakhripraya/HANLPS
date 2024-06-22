import weaviate as weaviate_lib
from weaviate.classes.tenants import Tenant
from configs.config import OPENAI_API_KEY
from src.interactor.interfaces.weaviate.api import WeaviateAPIInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.weaviate.schema.schema import WeaviateSchemasManagement
from src.infra.langchain.document_loader.document_loader import LangchainDocumentLoader
from src.infra.langchain.text_splitter.text_splitter import LangchainTextSplitter
from src.domain.constants import MESSAGES_COLLECTION_NAME,BUILDINGS_COLLECTION_NAME

class WeaviateAPI(WeaviateAPIInterface):
    """ WeaviateAPI class.
    """

    def __init__(self, logger: LoggerInterface) -> None: 
        try:
            self._logger = logger
            # connect Weaviate Cluster
            self._logger.log_info("Initializing Weaviate client")
            self._weaviate_client = weaviate_lib.connect_to_local(headers={
                "X-OpenAI-Api-Key": OPENAI_API_KEY
            })
            self._logger.log_info("Weaviate client successfully connected")
            
            # init schemas
            self._logger.log_info("Deleting all existing Weaviate collections")
            self._weaviate_client.collections.delete(MESSAGES_COLLECTION_NAME)
            self._weaviate_client.collections.delete(BUILDINGS_COLLECTION_NAME)
            
            self._logger.log_info("Creating new Weaviate collections")
            schema = WeaviateSchemasManagement(self._weaviate_client, self._logger)
            schema.create_collections()

            self._logger.log_info("Weaviate client successfully initialized")
        except Exception as e:
            if self._weaviate_client is not None:
                self._weaviate_client.close()
            logger.log_critical(f"Failed to start weaviate client, ERROR: {e}")
            
    def create_new_messages_tenant(self, tenant) -> None:
        """ 
        Create new tenant for messages collection
        :param tenant: tenant name.
        """
        # migrate data object
        try:
            self._logger.log_info(f"[{tenant}]: Creating new tenants")
            self._logger.log_info(f"[{tenant}]: Loading documents")
            loader = LangchainDocumentLoader("pdf", 'pdfs', "**/*.pdf")
            data = loader.execute()

            text_splitter = LangchainTextSplitter(128,0)
            docs = text_splitter.execute(data)
            
            count = 0
            self._logger.log_info(f"[{tenant}]: {count}/{len(docs)} Loaded")
            messages_collection =  self._weaviate_client.collections.get(MESSAGES_COLLECTION_NAME)
            messages_collection.tenants.create(
                Tenant(name=tenant)
            )
            
            messages_collection_with_tenant = messages_collection.with_tenant(tenant)
            for doc in docs:
                uuid = messages_collection_with_tenant.data.insert({
                    "content": doc.page_content,
                })
                
                count += 1
                self._logger.log_info(f"[{tenant}]: [{uuid}]: Document Loaded")
                self._logger.log_info(f"[{tenant}]: {count}/{len(docs)} Loaded")
                
            self._logger.log_info("Successfully load documents")
            self._logger.log_info(f"[{tenant}]: Successfully created new tenant")
        except Exception as e: 
            self._logger.log_exception(f"Failed to create new tenant, ERROR: {e}")