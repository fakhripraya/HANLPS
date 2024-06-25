""" Module for WeaviateAPI
"""

import weaviate as weaviate_lib
from configs.config import OPENAI_API_KEY, GEMINI_API_KEY
from src.domain.constants import OPENAI, GEMINI
from src.interactor.interfaces.weaviate.api import WeaviateAPIInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.weaviate.schema.schema import WeaviateSchemasManagement
from src.infra.langchain.document_loader.document_loader import LangchainDocumentLoader
from src.domain.constants import BUILDINGS_COLLECTION_NAME

class WeaviateAPI(WeaviateAPIInterface):
    """ WeaviateAPI class.
    """

    def __init__(self, with_generative: str | None, logger: LoggerInterface) -> None: 
        try:
            self._weaviate_client = None
            self._logger = logger
            # connect Weaviate Cluster
            self._logger.log_info("Initializing Weaviate client")

            if(with_generative == OPENAI):
                self.connect_with_openai()
            elif(with_generative == GEMINI):
                self.connect_with_google()
            else:
                self._weaviate_client = weaviate_lib.connect_to_local()
            
            self._logger.log_info("Weaviate client successfully connected")
            
            # init schemas
            self._logger.log_info("Deleting all existing Weaviate collections")
            self._weaviate_client.collections.delete(BUILDINGS_COLLECTION_NAME)
            
            self._logger.log_info("Creating new Weaviate collections")
            schema = WeaviateSchemasManagement(self._weaviate_client, self._logger)
            schema.create_collections()

            # load initial documents
            self.load_buildings_from_document_csv()
            
            self._logger.log_info("Weaviate client successfully initialized")
        except Exception as e:
            if self._weaviate_client is not None:
                self._weaviate_client.close()
            logger.log_critical(f"Failed to start weaviate client, ERROR: {e}")
            
    def connect_with_openai(self) -> None:
        """ 
        Connect the weaviate instance with openai module
        """
        self._weaviate_client = weaviate_lib.connect_to_local(headers={
            "X-OpenAI-Api-Key": OPENAI_API_KEY
         })
    
    def connect_with_google(self) -> None:
        """ 
        Connect the weaviate instance with google module
        """
        self._weaviate_client = weaviate_lib.connect_to_local(headers={
             "X-Google-Studio-Api-Key": GEMINI_API_KEY,
         })
            
    def load_buildings_from_document_csv(self) -> None:
        """ 
        Load and insert new objects of building and insert it to db from document csv
        """
        # migrate data object
        try:
            self._logger.log_info(f"Loading documents")
            loader = LangchainDocumentLoader("csv", './csvs/sheet.csv', "**/*.csv")
            docs = loader.execute()

            # text_splitter = LangchainTextSplitter(128,0)
            # docs = text_splitter.execute(data)
            
            self._logger.log_info(f"0/{len(docs)-1} Loaded")
            buildings_collection =  self._weaviate_client.collections.get(BUILDINGS_COLLECTION_NAME)
            for idx, doc in enumerate(docs):
                if(idx == 0): continue
                uuid = buildings_collection.data.insert({
                    "property_title": doc["property_title"],
                    "property_address": doc["property_address"],
                    "property_description": doc["property_description"],
                    "housing_price": float(doc["housing_price"]),
                    "owner_name": doc["owner_name"],
                    "owner_whatsapp": doc["owner_whatsapp"],
                    "owner_phone_number": doc["owner_phone_number"],
                    "owner_email": doc["owner_email"],
                    "image_url": doc["image_url"],
                })
                
                self._logger.log_info(f"[{uuid}]: Document Loaded")
                self._logger.log_info(f"{idx}/{len(docs)-1} Loaded")
                
            self._logger.log_info("Successfully load documents")
        except Exception as e: 
            self._logger.log_exception(f"Failed to load documents, ERROR: {e}")
            raise Exception(e)