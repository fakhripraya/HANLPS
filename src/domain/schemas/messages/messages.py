import weaviate.classes as wvc
from weaviate.client import WeaviateClient

def create_messages_vectordb_schema(client: WeaviateClient) -> None:
    collection_name = "Messages"
    if not client.collections.exists(collection_name):
        new_collection = client.collections.create(
            name=collection_name,
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
            generative_config=wvc.config.Configure.Generative.openai(),
            properties=[
                wvc.config.Property(
                    name="content",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=True,
                    tokenization=wvc.config.Tokenization.WHITESPACE
                ),
            ],
            # Configure the vector index
            vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
                distance_metric=wvc.config.VectorDistances.COSINE,
                quantizer=wvc.config.Configure.VectorIndex.Quantizer.pq(segments=192),
            ),
            # Configure the inverted index
            inverted_index_config=wvc.config.Configure.inverted_index(
                index_null_state=True,
                index_property_length=True,
                index_timestamps=True,
            ),
        )
        
        print(new_collection)