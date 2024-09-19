""" Module for WeaviateAPI
"""

import json
import weaviate as weaviate_lib
from weaviate.config import AdditionalConfig, ConnectionConfig , Timeout
from configs.config import (
    OPENAI_API_KEY,
    GEMINI_API_KEY,
    OPENAI_ORGANIZATION_ID,
    WEAVIATE_GRPC_HOST,
    WEAVIATE_GRPC_PORT,
    WEAVIATE_REST_HOST,
    WEAVIATE_REST_PORT,
    WEAVIATE_SECURE
)
from src.domain.constants import OPENAI, GEMINI
from src.interactor.interfaces.repositories.weaviate.api import WeaviateAPIInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.repositories.weaviate.schema.schema import WeaviateSchemasManagement
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
            self._weaviate_client.collections.delete(BUILDING_CHUNKS_COLLECTION_NAME)
            
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
      
    def connect_to_server(self, with_modules, module_used) -> weaviate_lib.WeaviateClient:
        if with_modules == 1 and module_used == OPENAI:
            return self.connect_with_openai()
        elif with_modules == 1 and module_used == GEMINI:
            return self.connect_with_google()
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
        return weaviate_lib.connect_to_custom(
            http_host=WEAVIATE_REST_HOST,
            http_port=WEAVIATE_REST_PORT,
            http_secure=False,
            grpc_host=WEAVIATE_GRPC_HOST,
            grpc_port=WEAVIATE_GRPC_PORT,
            grpc_secure=False,
            headers={
                "X-OpenAI-Api-Key": OPENAI_API_KEY,
                "X-OpenAI-Organization": OPENAI_ORGANIZATION_ID
            },
            additional_config=AdditionalConfig(
                connection=ConnectionConfig(
                    session_pool_max_retries=3,
                ),
                timeout=Timeout(query=60, insert=120),
            )
        )
    
    def connect_with_google(self) -> weaviate_lib.WeaviateClient:
        """ 
        Connect the weaviate instance with google module
        """
        # Currently has bug to use this header, only vertex is avail for now
        self._logger.log_info("Connecting weaviate client with Google")
        return weaviate_lib.connect_to_custom(
            http_host=WEAVIATE_REST_HOST,
            http_port=WEAVIATE_REST_PORT,
            http_secure=False,
            grpc_host=WEAVIATE_GRPC_HOST,
            grpc_port=WEAVIATE_GRPC_PORT,
            grpc_secure=False,
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
            self.load_data_to_db(docs)
        except Exception as e: 
            self._logger.log_exception(f"Failed to load csvs documents to weaviate, ERROR: {e}")
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
                if isinstance(docs, list) and all(isinstance(item, dict) for item in docs):
                    self.load_data_to_db(docs)
                else:
                    raise TypeError("The loaded data is not of type list[dict]")
        except Exception as e: 
            self._logger.log_exception(f"Failed to load json documents to weaviate, ERROR: {e}")
            raise Exception(e)
        
    def load_data_to_db(self, docs) -> None:
        try:
            self._logger.log_info(f"0/{len(docs)} Loaded")
            buildings_collection =  self._weaviate_client.collections.get(BUILDINGS_COLLECTION_NAME)
            building_chunks_collection =  self._weaviate_client.collections.get(BUILDING_CHUNKS_COLLECTION_NAME)
            
            temp_building = []
            self._logger.log_info("Loading documents")
            with buildings_collection.batch.dynamic() as building_batch:
                for idx, doc in enumerate(docs):
                    uuid = building_batch.add_object(
                        properties={
                            "buildingTitle": doc["building_title"],
                            "buildingAddress": doc["building_address"],
                            "buildingDescription": doc["building_description"],
                            "housingPrice": float(doc["housing_price"]),
                            "ownerName": doc["owner_name"],
                            "ownerWhatsapp": doc["owner_whatsapp"],
                            "ownerPhoneNumber": doc["owner_phone_number"],
                            "ownerEmail": doc["owner_email"],
                            "imageURL": str(doc["image_urls"]),
                        }
                    )
                    
                    temp_building.append({
                        "id": uuid,
                        "chunks": list(doc["building_proximity"]) + list(doc["building_facility"]),
                    })
                    self._logger.log_info(f"[{uuid}]: Document Loaded")
                    self._logger.log_info(f"{idx + 1}/{len(docs)} Loaded")
            failed_objs = buildings_collection.batch.failed_objects
            self._logger.log_info(f"Document failed batch objects load: {failed_objs}")
            
            temp_building_to_be_refered = []
            self._logger.log_info("Loading chunks")
            with building_chunks_collection.batch.dynamic() as chunk_batch:
                for idx, doc in enumerate(temp_building):
                    temp_chunk_uuids = []
                    self._logger.log_info(f"{[doc["id"]]}: Loading chunk")
                    for i, obj in enumerate(doc["chunks"]):
                        self._logger.log_info(f"[Object - {i + 1}]: {obj}")
                        chunk_uuid = chunk_batch.add_object(
                            properties={
                                "chunk": obj,
                            },
                        )
                        temp_chunk_uuids.append({
                            "chunk_uuid": chunk_uuid,
                        })
                        self._logger.log_info(f"[{chunk_uuid}]: Chunk Loaded")
                        
                    temp_building_to_be_refered.append({
                        "id": doc["id"],
                        "chunk_uuids": temp_chunk_uuids,
                    })
            failed_chunk_objs = building_chunks_collection.batch.failed_objects
            self._logger.log_info(f"Chunks failed batch objects load: {failed_chunk_objs}")
                   
            self._logger.log_info("Adding chunks as document references")
            with building_chunks_collection.batch.dynamic() as reference_batch:
                for idx, doc in enumerate(temp_building_to_be_refered):
                    for i, obj in enumerate(doc["chunk_uuids"]):
                        self._logger.log_info(f"[{doc["id"]}]: Adding chunk {obj["chunk_uuid"]} as reference")
                        reference_batch.add_reference(
                            from_property="hasBuilding",
                            from_uuid=obj["chunk_uuid"],
                            to=doc["id"],
                        )
                        self._logger.log_info(f"[{obj["chunk_uuid"]}]: Added as reference")
                    self._logger.log_info(f"{idx + 1}/{len(docs)} documents done adding references")
            failed_references = building_chunks_collection.batch.failed_references
            self._logger.log_info(f"Building to Chunk references failed batch objects link: {failed_references}")
            
            self._logger.log_info("Successfully load documents")
        except Exception as e: 
            self._logger.log_exception(f"Failed to load documents, ERROR: {e}")
            raise Exception(e)
          
    def close_connection_to_server(self) -> None:
        """Close the connection to Weaviate server"""
        if self._weaviate_client and self._weaviate_client.is_live:
            self._weaviate_client.close()