import weaviate.classes as wvc
from weaviate.client import WeaviateClient
from src.domain.constants import BUILDINGS_COLLECTION_NAME, OPENAI
from src.interactor.interfaces.logger.logger import LoggerInterface
from configs.config import (
    MODULE_USED,
    USE_MODULE,
    OPENAI_MODEL
)

text2vec_transformers = [
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
    ]

text2vec_openai = [
        wvc.config.Configure.NamedVectors.text2vec_openai( 
            name="building_details", source_properties=[
                "building_title",
                "building_address",
                "building_proximity",
                "building_facility",
            ],
            model="text-embedding-3-small",
        ),
        wvc.config.Configure.NamedVectors.text2vec_openai( 
            name="building_address", source_properties=[
                "building_address",
                "building_proximity",
            ],
            model="text-embedding-3-small",
        ),
    ]

def define_transformers():
    if int(USE_MODULE) == 1 and MODULE_USED == OPENAI:
        return text2vec_openai
    else: 
        return text2vec_transformers

def define_generative():
    if int(USE_MODULE) == 1 and MODULE_USED == OPENAI:
        openai_generative = wvc.config.Configure.Generative.openai(
            model="gpt-3.5-turbo"
        )
        return openai_generative
    else: 
        return None
    
def create_buildings_vectordb_schema(client: WeaviateClient, logger: LoggerInterface) -> None:
    collection_name = BUILDINGS_COLLECTION_NAME    
    if not client.collections.exists(collection_name):
        new_collection = client.collections.create(
            name=collection_name,
            vectorizer_config=define_transformers(),
            generative_config=define_generative(),
            properties=[
                wvc.config.Property(
                    name="building_title",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WORD,
                ),
                wvc.config.Property(
                    name="building_address",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WORD,
                ),
                wvc.config.Property(
                    name="building_proximity",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WORD,
                ),
                wvc.config.Property(
                    name="building_facility",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WORD,
                ),
                wvc.config.Property(
                    name="building_description",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="housing_price",
                    data_type=wvc.config.DataType.NUMBER,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="owner_name",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="owner_whatsapp",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="owner_phone_number",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="owner_email",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
                wvc.config.Property(
                    name="image_url",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True
                ),
            ],
        )
        
        logger.log_info(f"Successfully create collection: {new_collection}")