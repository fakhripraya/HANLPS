""" This module is responsible for weaviate schemas management
"""

from src.domain.schemas.buildings.buildings import create_buildings_vectordb_schema
from src.domain.schemas.buildings.chunks import create_building_chunks_vectordb_schema
from src.interactor.interfaces.logger.logger import LoggerInterface
from weaviate.client import WeaviateClient


class WeaviateSchemasManagement:
    """This class is responsible for initializing schemas"""

    def __init__(self, client: WeaviateClient, logger: LoggerInterface):
        self._weaviate_client = client
        self._logger = logger

    def create_collections(
        self,
    ) -> None:
        """This method is responsible for schemas creation"""
        create_buildings_vectordb_schema(
            client=self._weaviate_client, logger=self._logger
        )
        create_building_chunks_vectordb_schema(
            client=self._weaviate_client, logger=self._logger
        )
