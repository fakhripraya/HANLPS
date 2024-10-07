from weaviate.collections.collection import Collection, CrossReferences
from weaviate.classes.query import QueryReference
from weaviate.collections.classes.types import WeaviateProperties
from weaviate.collections.classes.internal import QueryReturn
from weaviate.collections.classes.filters import _Filters


def query_building_with_building_as_reference(
    collection: Collection[WeaviateProperties, None],
    query: str,
    filters: _Filters,
    limit: int,
    offset: int,
) -> QueryReturn[WeaviateProperties, CrossReferences]:
    response = collection.query.hybrid(
        query=query,
        target_vector="buildingDetails",
        filters=filters,
        limit=limit,
        offset=offset,
        return_references=[
            QueryReference(include_vector=True, link_on="hasBuilding"),
        ],
    )

    return response


def query_building(
    collection: Collection[WeaviateProperties, None],
    query: str,
    filters: _Filters,
    limit: int,
    offset: int,
) -> QueryReturn[WeaviateProperties, CrossReferences]:
    response = collection.query.hybrid(
        query=query,
        target_vector="buildingDetails",
        filters=filters,
        limit=limit,
        offset=offset,
    )

    return response
