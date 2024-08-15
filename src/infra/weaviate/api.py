""" Module for WeaviateAPI
"""

import json
import weaviate as weaviate_lib
from weaviate.config import AdditionalConfig, ConnectionConfig , Timeout
from configs.config import OPENAI_API_KEY, GEMINI_API_KEY, OPENAI_ORGANIZATION_ID
from src.domain.constants import OPENAI, GEMINI, HUGGING_FACE
from src.interactor.interfaces.weaviate.api import WeaviateAPIInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.weaviate.schema.schema import WeaviateSchemasManagement
from src.infra.langchain.document_loader.document_loader import LangchainDocumentLoader
from src.domain.constants import BUILDINGS_COLLECTION_NAME, BUILDING_CHUNKS_COLLECTION_NAME

class WeaviateAPI(WeaviateAPIInterface):
    """ WeaviateAPI class.
    """

    def __init__(self, with_modules: int, module_used: str | None, logger: LoggerInterface) -> None: 
        try:
            self._weaviate_client = None
            self._logger = logger
            self._logger.log_info("Initializing Weaviate client")
            
            # connect to weaviate client to load document
            self._weaviate_client = self.connect_to_server(with_modules, module_used)
            self._logger.log_info("Weaviate client successfully connected")  
            
            # init schemas
            self._logger.log_info("Deleting all existing Weaviate collections")
            self._weaviate_client.collections.delete(BUILDINGS_COLLECTION_NAME)
            
            self._logger.log_info("Creating new Weaviate collections")
            schema = WeaviateSchemasManagement(self._weaviate_client, self._logger)
            schema.create_collections()

            # load initial documents
            self.load_buildings_from_document_json()
            
            self._logger.log_info("Weaviate client successfully initialized")
        except Exception as e:
            if self._weaviate_client is not None:
                self._weaviate_client.close()
            logger.log_critical(f"Failed to start weaviate client, ERROR: {e}")
        finally:
            self.close_connection_to_server()
      
    def connect_to_server(self, with_modules: int, module_used: str) -> weaviate_lib.WeaviateClient:
        if with_modules == 1 and module_used == OPENAI:
            return self.connect_with_openai()
        elif with_modules == 1 and module_used == GEMINI:
            return self.connect_with_google()
        elif with_modules == 1 and module_used == HUGGING_FACE:
            return self.connect_locally()
        else:
            return self.connect_locally()
            
    def connect_locally(self) -> weaviate_lib.WeaviateClient:
        """ 
        Connect the weaviate instance locally
        """
        self._logger.log_info("Connecting weaviate client with local vectorizer")
        return weaviate_lib.connect_to_local(
            additional_config=AdditionalConfig(
                connection=ConnectionConfig(
                    session_pool_max_retries=3,
                ),
                timeout=Timeout(query=60, insert=120),
            ),
        )
    
    def connect_with_openai(self) -> weaviate_lib.WeaviateClient:
        """ 
        Connect the weaviate instance with openai module
        """
        self._logger.log_info("Connecting weaviate client with OpenAI")
        return weaviate_lib.connect_to_local(
            headers={
                "X-OpenAI-Api-Key": OPENAI_API_KEY,
                "X-OpenAI-Organization": OPENAI_ORGANIZATION_ID
            },
            additional_config=AdditionalConfig(
                connection=ConnectionConfig(
                    session_pool_max_retries=3,
                ),
                timeout=Timeout(query=60, insert=120),
            ),
        )
    
    def connect_with_google(self) -> weaviate_lib.WeaviateClient:
        """ 
        Connect the weaviate instance with google module
        """
        # Currently has bug to use this header, only vertex is avail for now
        self._logger.log_info("Connecting weaviate client with Google")
        return weaviate_lib.connect_to_local(
            headers={
             "X-Google-Studio-Api-Key": GEMINI_API_KEY,
            },
            additional_config=AdditionalConfig(
                connection=ConnectionConfig(
                    session_pool_max_retries=3,
                ),
                timeout=Timeout(query=60, insert=120),
            ),
        )
            
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
            building_chunks_collection =  self._weaviate_client.collections.get(BUILDING_CHUNKS_COLLECTION_NAME)
            for idx, doc in enumerate(docs):
                if(idx == 0): continue
                
                uuid = buildings_collection.data.insert({
                    "buildingTitle": doc["building_title"],
                    "buildingAddress": doc["building_address"],
                    "buildingDescription": doc["building_description"],
                    "housingPrice": float(doc["housing_price"]),
                    "ownerName": doc["owner_name"],
                    "ownerWhatsapp": doc["owner_whatsapp"],
                    "ownerPhoneNumber": doc["owner_phone_number"],
                    "ownerEmail": doc["owner_email"],
                    "imageUrl": str(doc["image_urls"]),
                })
                
                building_proximity = list(doc["building_proximity"])
                building_facility = list(doc["building_facility"])

                longest = len(building_proximity) if len(building_proximity) > len(building_facility) else len(building_facility)
                
                for i in range(longest):
                    proximity_chunk = building_proximity[i] if i < len(building_proximity) else None
                    facility_chunk = building_facility[i] if i < len(building_facility) else None

                    chunks_uuid = building_chunks_collection.data.insert(
                        properties={
                            "buildingProximity": proximity_chunk,
                            "buildingFacility": facility_chunk,
                        },
                        references={"hasBuilding": uuid},
                    )
                
                self._logger.log_info(f"[{uuid}]: Document Loaded")
                self._logger.log_info(f"{idx}/{len(docs)-1} Loaded")
                
            self._logger.log_info("Successfully load documents")
        except Exception as e: 
            self._logger.log_exception(f"Failed to load documents, ERROR: {e}")
            raise Exception(e)
        
    def load_buildings_from_document_json(self) -> None:
        """ 
        Load and insert new objects of building and insert it to db from document csv
        """
        # migrate data object
        try:
            self._logger.log_info(f"Loading documents")  
            with open('./json/data.json', 'r', encoding='utf-8') as file:
                docs = json.load(file)["data"]

            # text_splitter = LangchainTextSplitter(128,0)
            # docs = text_splitter.execute(data)
            
            self._logger.log_info(f"0/{len(docs)-1} Loaded")
            buildings_collection =  self._weaviate_client.collections.get(BUILDINGS_COLLECTION_NAME)
            for idx, doc in enumerate(docs):
                if(idx == 0): continue
                uuid = buildings_collection.data.insert({
                    "buildingTitle": doc["building_title"],
                    "buildingAddress": doc["building_address"],
                    "buildingProximity": doc["building_proximity"],
                    "buildingFacility": doc["building_facility"],
                    "buildingDescription": doc["building_description"],
                    "housingPrice": float(doc["housing_price"]),
                    "ownerName": doc["owner_name"],
                    "ownerWhatsapp": doc["owner_whatsapp"],
                    "ownerPhoneNumber": doc["owner_phone_number"],
                    "ownerEmail": doc["owner_email"],
                    "imageUrl": str(doc["image_urls"]),
                })
                
                self._logger.log_info(f"[{uuid}]: Document Loaded")
                self._logger.log_info(f"{idx}/{len(docs)-1} Loaded")
                
            self._logger.log_info("Successfully load documents")
        except Exception as e: 
            self._logger.log_exception(f"Failed to load documents, ERROR: {e}")
            raise Exception(e)
          
    def close_connection_to_server(self) -> None:
        """Close the connection to Weaviate server"""
        if self._weaviate_client and self._weaviate_client.is_live:
            self._weaviate_client.close()