""" Module for WeaviateAPI
"""

import weaviate as weaviate_lib
from configs.config import OPENAI_API_KEY
from src.interactor.interfaces.weaviate.api import WeaviateAPIInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.weaviate.schema.schema import WeaviateSchemasManagement
from src.infra.langchain.document_loader.document_loader import LangchainDocumentLoader
from src.infra.langchain.text_splitter.text_splitter import LangchainTextSplitter
from src.domain.constants import BUILDINGS_COLLECTION_NAME

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
            self._weaviate_client.collections.delete(BUILDINGS_COLLECTION_NAME)
            
            self._logger.log_info("Creating new Weaviate collections")
            schema = WeaviateSchemasManagement(self._weaviate_client, self._logger)
            schema.create_collections()

            self._logger.log_info("Weaviate client successfully initialized")
        except Exception as e:
            if self._weaviate_client is not None:
                self._weaviate_client.close()
            logger.log_critical(f"Failed to start weaviate client, ERROR: {e}")
            
    def load_buildings_from_document(self) -> None:
        """ 
        Load and insert new objects of building and insert it to db from document pdf
        """
        #TODO: This has not finished
        # migrate data object
        try:
            self._logger.log_info(f"Loading documents")
            loader = LangchainDocumentLoader("pdf", 'pdfs', "**/*.pdf")
            data = loader.execute()

            text_splitter = LangchainTextSplitter(128,0)
            docs = text_splitter.execute(data)
            
            count = 0
            self._logger.log_info(f"{count}/{len(docs)} Loaded")
            buildings_collection =  self._weaviate_client.collections.get(BUILDINGS_COLLECTION_NAME)
            for doc in docs:
                uuid = buildings_collection.data.insert({
                    "property_title": doc.page_content,
                    "property_address": doc.page_content,
                    "property_description": doc.page_content,
                    "latitude": doc.page_content,
                    "longitude": doc.page_content,
                    "housing_price": doc.page_content,
                    "owner_name": doc.page_content,
                    "owner_whatsapp": doc.page_content,
                    "owner_phone_number": doc.page_content,
                    "owner_email": doc.page_content,
                    "created_at": doc.page_content,
                })
                
                count += 1
                self._logger.log_info(f"[{uuid}]: Document Loaded")
                self._logger.log_info(f"{count}/{len(docs)} Loaded")
                
            self._logger.log_info("Successfully load documents")
        except Exception as e: 
            self._logger.log_exception(f"Failed to load documents, ERROR: {e}")