import weaviate.classes as wvc
from weaviate.client import WeaviateClient
from src.domain.constants import BUILDINGS_COLLECTION_NAME
from src.interactor.interfaces.logger.logger import LoggerInterface

def create_buildings_vectordb_schema(client: WeaviateClient, logger: LoggerInterface) -> None:
    collection_name = BUILDINGS_COLLECTION_NAME
    if not client.collections.exists(collection_name):
        new_collection = client.collections.create(
            name=collection_name,
            vectorizer_config=[
                wvc.config.Configure.NamedVectors.text2vec_transformers( 
                    name="building_details", source_properties=[
                        "building_title",
                        "building_address",
                        "building_description",
                        "housing_price"
                    ]
                ),
                wvc.config.Configure.NamedVectors.text2vec_transformers( 
                    name="building_title", source_properties=[
                        "building_title",
                    ]
                ),
                wvc.config.Configure.NamedVectors.text2vec_transformers( 
                    name="building_address", source_properties=[
                        "building_address",
                    ]
                ),
                wvc.config.Configure.NamedVectors.text2vec_transformers( 
                    name="building_description", source_properties=[
                        "building_description",
                    ]
                ),
                wvc.config.Configure.NamedVectors.text2vec_transformers( 
                    name="housing_price", source_properties=[
                        "housing_price",
                    ]
                ),
            ],
            properties=[
                wvc.config.Property(
                    name="building_title",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WHITESPACE,
                    index_searchable=True
                ),
                wvc.config.Property(
                    name="building_address",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WHITESPACE,
                    index_searchable=True 
                ),
                wvc.config.Property(
                    name="building_description",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WHITESPACE,
                    index_searchable=True 
                ),
                wvc.config.Property(
                    name="housing_price",
                    data_type=wvc.config.DataType.NUMBER,
                ),
                wvc.config.Property(
                    name="owner_name",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                ),
                wvc.config.Property(
                    name="owner_whatsapp",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                ),
                wvc.config.Property(
                    name="owner_phone_number",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                ),
                wvc.config.Property(
                    name="owner_email",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                ),
                wvc.config.Property(
                    name="image_url",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                ),
            ],
        )
        
        logger.log_info(f"Successfully create collection: {new_collection}")