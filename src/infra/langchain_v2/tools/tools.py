import time
import json

from configs.config import (
    USE_MODULE,
    MODULE_USED,
)
from src.domain.enum.tool_types.tool_types import ToolType
from src.domain.entities.message.message import Message
from src.domain.constants import (
    BUILDINGS_COLLECTION_NAME,
    BUILDING_CHUNKS_COLLECTION_NAME,
)

from src.domain.entities.message.message import Message
from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter
from src.domain.entities.building.building import Building
from src.infra.geocoding.api import NominatimGeocodingAPI
from src.interactor.interfaces.logger.logger import LoggerInterface

# Weaviate
from src.infra.repositories.weaviate.api import WeaviateAPI
from src.infra.repositories.weaviate.query_parser.query_parser import QueryParser
from src.infra.repositories.weaviate.query.query import (
    query_building_with_building_as_reference,
    query_building,
)
from src.infra.repositories.weaviate.filters.buildings.buildings import (
    append_housing_price_filters,
    append_building_facility_filters,
    append_building_note_filters,
    append_building_geolocation_filter,
)
from weaviate.classes.query import Filter
from weaviate.collections.collection import CrossReferences
from weaviate.collections.classes.types import WeaviateProperties
from weaviate.collections.classes.internal import QueryReturn, Object


class BoardingHouseAgentTools:
    def __init__(
        self, logger: LoggerInterface, session_id: str
    ):
        self._logger = logger
        self._session_id = session_id
        self._query_parser = QueryParser()

    def analyze_nearby_poi_by_address_input(self, input):
        return self._analyze_input(input, ToolType.SEARCH_POINT_OF_INTEREST.value)

    def analyze_specific_search_input(self, input):
        return self._analyze_input(input, ToolType.SEARCH_SPECIFIC_LOCATION.value)

    def analyze_save_location_input(self, input):
        return self._analyze_input(input, ToolType.SAVE_LOCATION.value)

    def analyze_get_direction(self, input):
        return self._analyze_input(input, ToolType.GET_DIRECTION.value)

    def search_nearby_poi_by_address(self, buildings_filter: BuildingsFilter):
        """
        Search for nearby POI of the given address.

        :param buildings_filter: Object containing address or proximity filter.
        :return: Message.
        """
        filter_array = self._prepare_filters(buildings_filter)
        self._logger.log_debug(f"[{self._session_id}]: {buildings_filter}")

        try:
            geocode_data = self._perform_geocoding(buildings_filter)
            lat_long = {"lat": geocode_data["lat"], "long": geocode_data["lon"]}
            filter_array["building_geolocation"] = (
                lambda distance: append_building_geolocation_filter(lat_long, distance)
            )
        except ValueError as e:
            self._logger.log_warning(f"[{self._session_id}]: {e}")

        location_query = self._build_query(
            ["building_title", "building_address", "building_proximity"],
            buildings_filter.__dict__,
        )

        facility_query = self._build_query(
            ["building_title", "building_facility", "building_note"],
            buildings_filter.__dict__,
        )

        return self._vector_db_retrieval(filter_array, facility_query, location_query)


    def search_specific_by_address(self, buildings_filter: BuildingsFilter):
        """
        Search for a specific place by address.

        :param buildings_filter: Object containing address or proximity filter.
        :return: Message.
        """
        geocode_data = self._perform_geocoding(buildings_filter)
        return Message(output_info=geocode_data, action=ToolType.SEARCH_POINT_OF_INTEREST.value)

    def save_location(self, buildings_filter: BuildingsFilter):
        """
        Temporarily save location data 

        :param buildings_filter: Object containing address or proximity filter.
        :return: Message.
        """
        return Message(output_building_info=buildings_filter, action=ToolType.SAVE_LOCATION.value)

    def get_direction(self, buildings_filter: BuildingsFilter):
        """
        Get the destination latitude longitude.

        :param buildings_filter: Object containing address or proximity filter.
        :return: Message.
        """
        geocode_data = self._perform_geocoding(buildings_filter)
        return Message(output_info=geocode_data, action=ToolType.GET_DIRECTION.value)

    def _analyze_input(self, input, input_code):
        """
        Helper method to process input and format the output JSON.

        :param input: The raw input to be processed.
        :param input_code: The input code for the specific operation.
        :return: Formatted JSON string.
        """
        result = str(input).strip("`").strip("json").strip("`").strip()
        try:
            data = json.loads(result)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON input: {e}")

        return json.dumps({
            "input_code": input_code,
            "input_field": data
        }, indent=4)

    def _perform_geocoding(self, buildings_filter: BuildingsFilter) -> dict:
        """
        Perform geocoding using NominatimGeocodingAPI.

        :param geo_query: The address or proximity to geocode.
        :return: Geocode data as a dictionary or raises ValueError if no valid data is found.
        """
        geo_query = (
            buildings_filter.building_address
            or buildings_filter.building_proximity
            or buildings_filter.building_title
        )

        if not geo_query:
            raise ValueError("No valid address or proximity provided.")

        self._logger.log_debug(f"[{self._session_id}]: Performing geocoding for: {geo_query}")
        with NominatimGeocodingAPI(self._logger) as geocode_api:
            geocode_data = geocode_api.execute_geocode_by_address(geo_query)

            if geocode_data and "error" not in geocode_data:
                self._logger.log_debug(f"[{self._session_id}]: Got geocode data: {geocode_data}")
                return geocode_data
            else:
                raise ValueError(f"[{self._session_id}]: No valid geocode data for query: {geo_query}")

    def _vector_db_retrieval(
        self, filter_array, facility_query="", location_query=""
    ) -> Message:
        """
        Vector database data retrieval process
        :param prompt: chat message to be analyzed.
        :param session_id: session id of the chat.
        :param filter_array: filters that needed for prompt analysis.
        :param facility_query: query by facility to retrieve vector data from weaviate.
        :param location_query: query by location to retrieve vector data from weaviate.
        """
        limit, offset, retries, max_retries = 5, 0, 0, 3
        start_time, building_list, seen_uuids = time.time(), [], set()
        geolocation_stages, geolocation_stage_index = [3000], 0

        with WeaviateAPI(self._logger) as weaviate_client:
            while retries < max_retries:
                connected, building_collection, building_chunk_collection = (
                    self._connect_to_collections(weaviate_client) or (None, None, None)
                )
                try:
                    while len(building_list) < limit:
                        filters, with_geofilter = None, self._geofilter_check(
                            geolocation_stages, geolocation_stage_index, filter_array
                        )

                        if with_geofilter:
                            filters = self._apply_geofilter_conditions(
                                filter_array,
                                distance=geolocation_stages[geolocation_stage_index],
                            )

                            self._logger.log_debug(
                                f'[{self._session_id}]: Executing facility query "{facility_query}"'
                            )
                            response = query_building(
                                building_collection,
                                facility_query,
                                filters,
                                limit,
                                offset,
                            )
                        else:
                            filters = self._apply_non_geofilter_conditions(filter_array)

                            self._logger.log_debug(
                                f'[{self._session_id}]: Executing location query "{location_query}"'
                            )
                            response = query_building_with_building_as_reference(
                                building_chunk_collection,
                                location_query,
                                filters,
                                limit,
                                offset,
                            )

                        if not response.objects:
                            if self._handle_empty_geosearch(
                                self._session_id,
                                with_geofilter,
                                geolocation_stages,
                                geolocation_stage_index,
                                facility_query,
                                location_query,
                            ):
                                geolocation_stage_index += 1
                                offset = 0
                            else:
                                break
                        else:
                            self._process_response(
                                with_geofilter,
                                response,
                                building_list,
                                seen_uuids,
                                limit,
                            )
                            if len(building_list) >= limit:
                                break
                        offset += limit

                    self._log_query_execution_time(
                        self._session_id, start_time, building_list
                    )
                    break

                except Exception as e:
                    if retries >= max_retries:
                        self._logger.log_exception(
                            f"[{self._session_id}]: Weaviate query failed after {max_retries} retries. {e}"
                        )
                    else:
                        self._logger.log_warning(
                            f"[{self._session_id}]: Query attempt {retries} failed. Error: {e}"
                        )
                        retries += 1
                finally:
                    weaviate_client.close_connection_to_server(connected)

        return Message(output_building_info=building_list, action=ToolType.SEARCH_SPECIFIC_LOCATION.value)

    def _build_query(self, fields, filter_data):
        if any(filter_data[field] for field in fields):
            return self._query_parser.execute(
                {field: filter_data[field] for field in fields}
            )
        return None

    def _prepare_filters(self, buildings_filter: BuildingsFilter):
        filter_array = None
        filter_array = {
            "housing_price": lambda with_reference: append_housing_price_filters(
                buildings_filter, [], with_reference
            ),
            "building_facility": append_building_facility_filters(buildings_filter, []),
            "building_note": append_building_note_filters(buildings_filter, []),
        }

        return filter_array

    def _connect_to_collections(self, weaviate_client: WeaviateAPI):
        """Connect to the necessary collections for querying."""
        connected = weaviate_client.connect_to_server(int(USE_MODULE), MODULE_USED)
        if connected is None:
            raise RuntimeError(
                f"Runtime Error - Failed to connect to Weaviate Server Instance"
            )

        building_collection = connected.collections.get(BUILDINGS_COLLECTION_NAME)
        building_chunk_collection = connected.collections.get(
            BUILDING_CHUNKS_COLLECTION_NAME
        )
        return connected, building_collection, building_chunk_collection

    def _geofilter_check(
        self,
        geolocation_stages: list[int],
        geolocation_stage_index: int,
        filter_array: dict[str, list],
    ):
        """Check if geolocation filter can be applied."""
        return callable(
            filter_array.get("building_geolocation")
        ) and geolocation_stage_index < len(geolocation_stages)

    def _apply_geofilter_conditions(
        self, filter_array: dict[str, list], distance: float
    ):
        """Apply geolocation and housing price filters."""
        housing_price_filter = filter_array["housing_price"](False)
        filters = Filter.all_of(housing_price_filter) if housing_price_filter else None
        geofilter = filter_array["building_geolocation"](distance)
        return filters & geofilter if filters else geofilter

    def _apply_non_geofilter_conditions(self, filter_array: dict[str, list]):
        """Apply non-geolocation filters."""
        facility_filters = (
            Filter.any_of(filter_array["building_facility"])
            if filter_array["building_facility"]
            else None
        )
        note_filter = (
            Filter.any_of(filter_array["building_note"])
            if filter_array["building_note"]
            else None
        )

        housing_price_filter = filter_array["housing_price"](True)
        price_filters = (
            Filter.all_of(housing_price_filter) if housing_price_filter else None
        )
        filters = facility_filters & note_filter if facility_filters else note_filter
        filters = filters & price_filters if filters else price_filters
        return filters

    def _handle_empty_geosearch(
        self,
        session_id: str,
        with_geofilter: bool,
        geolocation_stages: list[int],
        geolocation_stage_index: int,
        facility_query: str,
        location_query: str,
    ):
        """Handle cases with no results."""
        if with_geofilter:
            self._logger.log_debug(
                f"[{session_id}]: No results at {geolocation_stages[geolocation_stage_index]} meters for query: {facility_query}"
            )
            return True
        self._logger.log_debug(
            f"[{session_id}]: No results for query: {location_query}"
        )
        return False

    def _process_response(
        self,
        with_geofilter: bool,
        response: QueryReturn[WeaviateProperties, CrossReferences],
        building_list: list,
        seen_uuids: set,
        limit: int,
    ):
        """
        Process each object in the response and add to building_list.
        loop through the response objects along with filtering which object should be appended
        """
        for _, obj in enumerate(response.objects):
            if with_geofilter:
                self._add_building_instance(obj, seen_uuids, building_list)
            else:
                for ref_obj in obj.references["hasBuilding"].objects:
                    if ref_obj.uuid not in seen_uuids:
                        self._add_building_instance(
                            ref_obj,
                            seen_uuids,
                            building_list,
                        )
            if len(building_list) >= limit:
                break

    def _add_building_instance(
        self,
        obj: Object[WeaviateProperties, CrossReferences],
        seen_uuids: set,
        building_list: list,
    ):
        """Add a building instance to the list after checking for duplicates."""
        seen_uuids.add(obj.uuid)
        building_instance = Building(
            building_title=obj.properties["buildingTitle"],
            building_address=obj.properties["buildingAddress"],
            building_description=obj.properties["buildingDescription"],
            housing_price=obj.properties["housingPrice"],
            owner_name=obj.properties["ownerName"],
            owner_email=obj.properties["ownerEmail"],
            owner_whatsapp=obj.properties["ownerWhatsapp"],
            owner_phone_number=obj.properties["ownerPhoneNumber"],
            image_url=obj.properties["imageURL"],
        )
        building_list.append(building_instance)

    def _log_query_execution_time(
        self, session_id: str, start_time: float, building_list: list
    ):
        """Log the time taken for the query and total objects found."""
        elapsed_time = time.time() - start_time
        self._logger.log_info(
            f"[{session_id}]: Query completed in {elapsed_time:.2f} seconds. Total buildings found: {len(building_list)}"
        )
