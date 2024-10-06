import weaviate.classes as wvc
from weaviate.client import WeaviateClient
from src.domain.constants import (
    BUILDINGS_COLLECTION_NAME,
    OPENAI,
)
from src.interactor.interfaces.logger.logger import LoggerInterface
from configs.config import (
    MODULE_USED,
    USE_MODULE,
    OPENAI_GENERATIVE_MODEL,
    OPENAI_TRANSFORMERS_MODEL,
)

text2vec_transformers = [
    wvc.config.Configure.NamedVectors.text2vec_transformers(
        name="buildingDetails",
        source_properties=[
            "buildingDescription",
        ],
    ),
]

text2vec_openai = [
    wvc.config.Configure.NamedVectors.text2vec_openai(
        name="buildingDetails",
        source_properties=[
            "buildingDescription",
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


def create_buildings_vectordb_schema(
    client: WeaviateClient, logger: LoggerInterface
) -> None:
    collection_name = BUILDINGS_COLLECTION_NAME
    if not client.collections.exists(collection_name):
        new_collection = client.collections.create(
            name=collection_name,
            properties=[
                wvc.config.Property(
                    name="buildingTitle",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name="buildingAddress",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name="buildingDescription",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WORD,
                ),
                wvc.config.Property(
                    name="buildingGeolocation",
                    data_type=wvc.config.DataType.GEO_COORDINATES,
                    vectorize_property_name=False,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name="housingPrice",
                    data_type=wvc.config.DataType.NUMBER,
                    vectorize_property_name=False,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name="ownerName",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name="ownerEmail",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name="ownerWhatsapp",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name="ownerPhoneNumber",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name="imageURL",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    skip_vectorization=True,
                ),
            ],
        )

        logger.log_info(f"Successfully create collection: {new_collection}")
