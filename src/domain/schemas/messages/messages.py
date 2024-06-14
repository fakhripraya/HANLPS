import weaviate.classes as wvc
from weaviate.client import WeaviateClient

def create_message_vectordb_schema(client: WeaviateClient) -> None:
    questions = client.collections.create(
        name="Messages",
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
        generative_config=wvc.config.Configure.Generative.openai(),
        properties=[
            wvc.config.Property(
                name="question",
                data_type=wvc.config.DataType.TEXT,
                vectorize_property_name=True,  # Include the property name ("question") when vectorizing
                tokenization=wvc.config.Tokenization.LOWERCASE  # Use "lowecase" tokenization
            ),
            wvc.config.Property(
                name="answer",
                data_type=wvc.config.DataType.TEXT,
                vectorize_property_name=False,  # Skip the property name ("answer") when vectorizing
                tokenization=wvc.config.Tokenization.WHITESPACE  # Use "whitespace" tokenization
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
    
    print(questions)