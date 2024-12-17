""" Module for WeaviateAPI
"""

import json
import weaviate as weaviate_lib
import traceback
from weaviate.config import AdditionalConfig, ConnectionConfig, Timeout
from configs.config import (
    OPENAI_API_KEY,
    GEMINI_API_KEY,
    OPENAI_ORGANIZATION_ID,
    WEAVIATE_GRPC_HOST,
    WEAVIATE_GRPC_PORT,
    WEAVIATE_REST_HOST,
    WEAVIATE_REST_PORT,
    USE_MODULE,
    MODULE_USED,
)
from src.domain.constants import OPENAI, GEMINI
from src.interactor.interfaces.repositories.weaviate.api import WeaviateAPIInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infra.repositories.weaviate.schema.schema import WeaviateSchemasManagement
from src.domain.constants import (
    BUILDINGS_COLLECTION_NAME,
    BUILDING_CHUNKS_COLLECTION_NAME,
)


class WeaviateAPI(WeaviateAPIInterface):
    """WeaviateAPI class."""

    def __init__(self, logger: LoggerInterface) -> None:
        self._logger = logger
        self._logger.log_info("Initializing Weaviate instance")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._logger.log_exception(f"[{exc_type}]: {exc_val}")
            self._logger.log_exception(f"Traceback: {traceback.format_tb(exc_tb)}")

    def migrate_datas(self) -> None:
        try:
            weaviate_client = None

            # connect to weaviate client to load document
            self._logger.log_info("Connecting to the Weaviate client")
            weaviate_client = self.connect_to_server(int(USE_MODULE), MODULE_USED)
            self._logger.log_info("Successfully connected")

            # init schemas
            self._logger.log_info("Migrating imported collections to the instance")
            self._logger.log_info("Deleting all existing collections")
            weaviate_client.collections.delete(BUILDINGS_COLLECTION_NAME)
            weaviate_client.collections.delete(BUILDING_CHUNKS_COLLECTION_NAME)

            self._logger.log_info("Creating new collections")
            schema = WeaviateSchemasManagement(weaviate_client, self._logger)
            schema.create_collections()

            # load initial documents
            self._logger.log_info("Load created collections into the instance")
            self.load_buildings_from_document_json(weaviate_client)

            self._logger.log_info(
                "Successfully migrate imported collections to the instance"
            )
        except Exception as e:
            if weaviate_client is not None:
                weaviate_client.close()
            self._logger.log_critical(
                f"Failed to Migrate weaviate collections, ERROR: {e}"
            )
        finally:
            self.close_connection_to_server(weaviate_client)

    def connect_to_server(
        self, with_modules, module_used
    ) -> weaviate_lib.WeaviateClient:
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
                "X-OpenAI-Organization": OPENAI_ORGANIZATION_ID,
            },
            additional_config=AdditionalConfig(
                connection=ConnectionConfig(
                    session_pool_max_retries=3,
                    session_pool_connections=20,
                    session_pool_maxsize=100,
                ),
                timeout=Timeout(query=60, insert=120),
            ),
            skip_init_checks=True,
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

    def load_buildings_from_document_json(self, weaviate_client) -> None:
        """
        Load and insert new objects of building and insert it to db from document csv
        """
        # migrate data object
        try:
            self._logger.log_info(f"Loading documents")
            with open("./json/data.json", "r", encoding="utf-8") as file:
                docs = json.load(file)["data"]
                if isinstance(docs, list) and all(
                    isinstance(item, dict) for item in docs
                ):
                    self.load_data_to_db(docs, weaviate_client)
                else:
                    raise TypeError("The loaded data is not of type list[dict]")
        except Exception as e:
            self._logger.log_exception(
                f"Failed to load json documents to weaviate, ERROR: {e}"
            )
            raise Exception(e)

    def load_data_to_db(self, docs, weaviate_client) -> None:
        try:
            self._logger.log_info(f"0/{len(docs)} Loaded")
            buildings_collection = weaviate_client.collections.get(
                BUILDINGS_COLLECTION_NAME
            )
            building_chunks_collection = weaviate_client.collections.get(
                BUILDING_CHUNKS_COLLECTION_NAME
            )

            temp_building = []
            self._logger.log_info("Inserting documents")
            with buildings_collection.batch.dynamic() as building_batch:
                for idx, doc in enumerate(docs):
                    uuid = building_batch.add_object(
                        properties={
                            "buildingTitle": doc["building_title"],
                            "buildingAddress": doc["building_address"],
                            "buildingDescription": doc["building_description"],
                            "buildingGeolocation": doc["building_geolocation"],
                            "housingPrice": float(doc["housing_price"]),
                            "ownerName": doc["owner_name"],
                            "ownerWhatsapp": doc["owner_whatsapp"],
                            "ownerPhoneNumber": doc["owner_phone_number"],
                            "ownerEmail": doc["owner_email"],
                            "imageURL": str(doc["image_urls"]),
                        }
                    )

                    temp_building.append(
                        {
                            "id": uuid,
                            "chunks": list(doc["building_proximity"])
                            + list(doc["building_facility"]),
                        }
                    )
                    self._logger.log_info(f"[{uuid}]: Document Loaded")
                    self._logger.log_info(f"{idx + 1}/{len(docs)} Loaded")
            failed_objs = buildings_collection.batch.failed_objects
            self._logger.log_info(f"Document failed batch objects load: {failed_objs}")

            temp_building_to_be_refered = []
            self._logger.log_info("Inserting Chunks")
            with building_chunks_collection.batch.dynamic() as chunk_batch:
                for idx, doc in enumerate(temp_building):
                    temp_chunk_uuids = []
                    self._logger.log_info(f"{[doc["id"]]}: Loading chunks")
                    for i, obj in enumerate(doc["chunks"]):
                        chunk_uuid = chunk_batch.add_object(
                            properties={
                                "chunk": obj,
                            },
                        )
                        temp_chunk_uuids.append(
                            {
                                "chunk_uuid": chunk_uuid,
                            }
                        )

                    temp_building_to_be_refered.append(
                        {
                            "id": doc["id"],
                            "chunk_uuids": temp_chunk_uuids,
                        }
                    )
                    self._logger.log_info(f"{[doc["id"]]}: Loaded chunks")
            failed_chunk_objs = building_chunks_collection.batch.failed_objects
            self._logger.log_info(
                f"Chunks failed batch objects load: {failed_chunk_objs}"
            )

            self._logger.log_info("Adding chunks as document references")
            with building_chunks_collection.batch.dynamic() as reference_batch:
                for idx, doc in enumerate(temp_building_to_be_refered):
                    for i, obj in enumerate(doc["chunk_uuids"]):
                        reference_batch.add_reference(
                            from_property="hasBuilding",
                            from_uuid=obj["chunk_uuid"],
                            to=doc["id"],
                        )
                    self._logger.log_info(
                        f"{idx + 1}/{len(docs)} documents done adding references"
                    )
            failed_references = building_chunks_collection.batch.failed_references
            self._logger.log_info(
                f"Building to Chunk references failed batch objects link: {failed_references}"
            )

            self._logger.log_info("Successfully load documents")
        except Exception as e:
            self._logger.log_exception(f"Failed to load documents, ERROR: {e}")
            raise Exception(e)

    def close_connection_to_server(self, weaviate_client) -> None:
        """Close the connection to Weaviate server"""
        if weaviate_client and weaviate_client.is_live:
            weaviate_client.close()
