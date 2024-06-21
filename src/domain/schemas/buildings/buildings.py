import weaviate.classes as wvc
from weaviate.client import WeaviateClient

def create_buildings_vectordb_schema(client: WeaviateClient) -> None:
    collection_name = "Buildings"
    if not client.collections.exists(collection_name):
        new_collection = client.collections.create(
            name=collection_name,
            vectorizer_config=[
                wvc.config.Configure.NamedVectors.text2vec_openai(
                    name="text_based_vect", source_properties=[
                        "property_title",
                        "property_address",
                        "property_description",
                        "latitude",
                        "longitude"
                    ]
                ),
                wvc.config.Configure.NamedVectors.text2vec_openai(
                    name="img_based_vect", source_properties=["image_embedding"]
                )
            ],
            generative_config=wvc.config.Configure.Generative.openai(),
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
                    name="latitude",
                    data_type=wvc.config.DataType.TEXT,
                ),
                wvc.config.Property(
                    name="longitude",
                    data_type=wvc.config.DataType.TEXT,
                ),
                wvc.config.Property(
                    name="housing_price",
                    data_type=wvc.config.DataType.NUMBER,
                    vectorize_property_name=False,
                ),
                wvc.config.Property(
                    name="owner_name",
                    data_type=wvc.config.DataType.TEXT,
                    vectorize_property_name=False,
                    tokenization=wvc.config.Tokenization.WHITESPACE
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
                    name="image_embedding",
                    data_type=wvc.config.DataType.BLOB,
                ),
                wvc.config.Property(
                    name="created_at",
                    data_type=wvc.config.DataType.DATE,
                ),
            ],
            vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
                distance_metric=wvc.config.VectorDistances.COSINE,
                quantizer=wvc.config.Configure.VectorIndex.Quantizer.pq(segments=192),
            ),
            inverted_index_config=wvc.config.Configure.inverted_index(
                index_null_state=True,
                index_property_length=True,
                index_timestamps=True,
            ),
        )
        
        print(new_collection)