import weaviate.classes as wvc
from weaviate.client import WeaviateClient
from src.domain.constants import MESSAGES_COLLECTION_NAME
from src.interactor.interfaces.logger.logger import LoggerInterface

def create_messages_vectordb_schema(client: WeaviateClient, logger: LoggerInterface) -> None:
    collection_name = MESSAGES_COLLECTION_NAME
    if not client.collections.exists(collection_name):
        new_collection = client.collections.create(
            name=collection_name,
            vectorizer_config=[
                wvc.config.Configure.NamedVectors.multi2vec_clip(
                    name="messages_text_image_vector",
                    text_fields=[
                            wvc.config.Multi2VecField(name="content", weight=1),
                        ]
                )
            ],
            generative_config=wvc.config.Configure.Generative.openai(),
            properties=[
                wvc.config.Property(
                    name="content",
                    data_type=wvc.config.DataType.TEXT,
                    tokenization=wvc.config.Tokenization.WHITESPACE
                ),
            ],
            multi_tenancy_config=wvc.config.Configure.multi_tenancy(True,auto_tenant_activation=True)
            # # Configure the vector index
            # vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
            #     distance_metric=wvc.config.VectorDistances.COSINE,
            #     quantizer=wvc.config.Configure.VectorIndex.Quantizer.pq(segments=192),
            # ),
            # # Configure the inverted index
            # inverted_index_config=wvc.config.Configure.inverted_index(
            #     index_null_state=True,
            #     index_property_length=True,
            #     index_timestamps=True,
            # ),
        )
        
        logger.log_info(f"Successfully create collection: {new_collection}")