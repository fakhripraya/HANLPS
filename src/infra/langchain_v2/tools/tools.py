from src.domain.pydantic_models.buildings_filter.buildings_filter import BuildingsFilter
from src.domain.entities.building.building import Building

from langchain.agents import Tool


def search_boarding_house(input):
    buildings_filter = BuildingsFilter(**input)
    self._logger.log_debug(f"[{session_id}]: Filters - {buildings_filter}")

    filter_array = self._prepare_filters(buildings_filter)

    building_instance = None
    with GeocodingAPI(self._logger) as obj:
        try:
            query = (
                buildings_filter.building_address
                if buildings_filter.building_address
                else buildings_filter.building_proximity
            )
            if query is not None:
                result = self._chat_completion.execute(
                    {
                        "prompts": query,
                    },
                    self._location_verifier_prompt_parser,
                    [location_verifier_template],
                ).get("address")

                geo_query = query if result in [None, "None"] else result
                self._logger.log_debug(f"[{session_id}]: Verified address: {geo_query}")
                geocode_data = obj.execute_geocode_by_address(geo_query)
                if len(geocode_data) > 0:
                    self._logger.log_debug(
                        f"[{session_id}]: Got geocode data: {geocode_data}"
                    )
                    lat_long = geocode_data[0]["geometry"]["location"]
                    filter_array["building_geolocation"] = (
                        lambda distance: append_building_geolocation_filter(
                            lat_long, distance
                        )
                    )

        except Exception as e:
            self._logger.log_exception(f"[{session_id}]: Error Geocode: {e}")

    location_query = None
    facility_query = None
    if any(
        [
            buildings_filter.building_title,
            buildings_filter.building_address,
            buildings_filter.building_proximity,
        ]
    ):
        building_instance = Building(
            building_title=buildings_filter.building_title,
            building_address=buildings_filter.building_address,
            building_proximity=buildings_filter.building_proximity,
        )
        location_query = self._query_parser.execute(building_instance.to_dict())

    if any(
        [
            buildings_filter.building_title,
            buildings_filter.building_facility,
            buildings_filter.building_note,
        ]
    ):
        facility_query_instance = Building(
            building_title=buildings_filter.building_title,
            building_facility=buildings_filter.building_facility,
            building_note=buildings_filter.building_note,
        )
        facility_query = self._query_parser.execute(facility_query_instance.to_dict())

    output = self.vector_db_retrieval(
        prompt, session_id, filter_array, facility_query, location_query
    )


def save_location(input):
    return "Location has been sucessfully saved"

 def vector_db_retrieval(
        self, prompt, session_id, filter_array, facility_query="", location_query=""
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
                                f'[{session_id}]: Executing facility query "{facility_query}"'
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
                                f'[{session_id}]: Executing location query "{location_query}"'
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
                                session_id,
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
                                session_id,
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
                        session_id, start_time, building_list
                    )
                    break

                except Exception as e:
                    if retries >= max_retries:
                        self._logger.log_exception(
                            f"[{session_id}]: Weaviate query failed after {max_retries} retries. {e}"
                        )
                    else:
                        self._logger.log_warning(
                            f"[{session_id}]: Query attempt {retries} failed. Error: {e}"
                        )
                        retries += 1
                finally:
                    weaviate_client.close_connection_to_server(connected)

        return self.feedback_prompt(prompt, session_id, found=building_list or True)



tools = [
    Tool(
        name="SearchBoardingHouse",
        func=search_boarding_house,
        description="Search for boarding houses based on the specified criteria.",
    ),
    Tool(
        name="SaveLocation",
        func=save_location,
        description="Save the location to the database",
    ),
]
