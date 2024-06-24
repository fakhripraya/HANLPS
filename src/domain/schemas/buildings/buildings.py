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
                wvc.config.Configure.NamedVectors.multi2vec_clip(
                    name="buildings_text_vector",
                    text_fields=[
                        wvc.config.Multi2VecField(name="property_title", weight=0.1),
                        wvc.config.Multi2VecField(name="property_address", weight=0.3),
                        wvc.config.Multi2VecField(name="property_description", weight=0.4),
                        wvc.config.Multi2VecField(name="housing_price", weight=0.2),
                    ]
                )
            ],
            properties=[
                wvc.config.Property(
                    name="property_title",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WHITESPACE 
                ),
                wvc.config.Property(
                    name="property_address",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WHITESPACE 
                ),
                wvc.config.Property(
                    name="property_description",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WHITESPACE 
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
            # vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
            #     distance_metric=wvc.config.VectorDistances.COSINE,
            #     quantizer=wvc.config.Configure.VectorIndex.Quantizer.pq(segments=192),
            # ),
            # inverted_index_config=wvc.config.Configure.inverted_index(
            #     index_null_state=True,
            #     index_property_length=True,
            #     index_timestamps=True,
            # ),
        )
        
        logger.log_info(f"Successfully create collection: {new_collection}")