import weaviate.classes as wvc
from weaviate.client import WeaviateClient
from src.domain.constants import BUILDINGS_COLLECTION_NAME, BUILDING_CHUNKS_COLLECTION_NAME, OPENAI
from src.interactor.interfaces.logger.logger import LoggerInterface
from configs.config import (
    MODULE_USED,
    USE_MODULE,
    OPENAI_GENERATIVE_MODEL,
    OPENAI_TRANSFORMERS_MODEL,
)

text2vec_transformers = [
        wvc.config.Configure.NamedVectors.text2vec_transformers( 
            name="buildingDetails", source_properties=[
                "buildingTitle",
                "buildingAddress",
                "buildingProximity",
                "buildingFacility",
            ],
        ),
        wvc.config.Configure.NamedVectors.text2vec_transformers( 
            name="buildingAddress", source_properties=[
                "buildingAddress",
                "buildingProximity",
            ],
        ),
    ]

text2vec_openai = [
        wvc.config.Configure.NamedVectors.text2vec_openai( 
            name="buildingDetails", source_properties=[
                "buildingTitle",
                "buildingAddress",
                "buildingProximity",
                "buildingFacility",
            ],
            model=OPENAI_TRANSFORMERS_MODEL,
        ),
        wvc.config.Configure.NamedVectors.text2vec_openai( 
            name="buildingAddress", source_properties=[
                "buildingAddress",
                "buildingProximity",
            ],
            model=OPENAI_TRANSFORMERS_MODEL,
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
            model=OPENAI_GENERATIVE_MODEL
        )
        return openai_generative
    else: 
        return None
    
def create_building_chunks_vectordb_schema(client: WeaviateClient, logger: LoggerInterface) -> None:
    collection_name = BUILDING_CHUNKS_COLLECTION_NAME  
    if not client.collections.exists(collection_name):
        new_collection = client.collections.create(
            name=collection_name,
            vectorizer_config=define_transformers(),
            generative_config=define_generative(),
            properties=[
                wvc.config.Property(
                    name="buildingProximity",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WORD,
                ),
                wvc.config.Property(
                    name="buildingFacility",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WORD,
                ),
            ],
            references=[
                wvc.config.ReferenceProperty(
                    name="hasBuilding",
                    target_collection=BUILDINGS_COLLECTION_NAME
                )
            ]
        )
        
        logger.log_info(f"Successfully create collection: {new_collection}")