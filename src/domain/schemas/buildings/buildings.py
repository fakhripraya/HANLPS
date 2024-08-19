import weaviate.classes as wvc
from weaviate.client import WeaviateClient
from src.domain.constants import BUILDINGS_COLLECTION_NAME, BUILDING_CHUNKS_COLLECTION_NAME
from src.interactor.interfaces.logger.logger import LoggerInterface
    
def create_buildings_vectordb_schema(client: WeaviateClient, logger: LoggerInterface) -> None:
    collection_name = BUILDINGS_COLLECTION_NAME    
    if not client.collections.exists(collection_name):
        new_collection = client.collections.create(
            name=collection_name,
            properties=[
                wvc.config.Property(
                    name="buildingTitle",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="buildingAddress",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="buildingDescription",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="housingPrice",
                    data_type=wvc.config.DataType.NUMBER,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="ownerName",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="ownerWhatsapp",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="ownerPhoneNumber",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="ownerEmail",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="imageURL",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
            ]
        )
        
        logger.log_info(f"Successfully create collection: {new_collection}")