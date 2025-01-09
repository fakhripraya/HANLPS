""" This module is responsible for all reverse geocoding method.
"""

import backoff
from requests import Session
from requests.exceptions import RequestException
from googlemaps import Client, geocoding
from googlemaps.exceptions import ApiError, TransportError, Timeout


class ReverseGeocodeModules:
    """This class is responsible for reverse geocoding method"""

    def __init__(
        self,
        client: Client,
    ):
        self._client = client

    @backoff.on_exception(
        backoff.expo,
        (ApiError, TransportError, Timeout),
        max_tries=3,
    )
    def execute(self, lat: str, long: str):
        """This method is to reverse geocode with the given geo datas.
        :param lat: The input latitude.
        :param long: The input longitude.
        :type lat: str
        :type long: str
        :return: str
        """
        result = geocoding.reverse_geocode(self._client, (lat, long))
        return result

class OSMReverseGeocodeModules:
    """This class is responsible for reverse geocoding method using osm"""

    def __init__(self, session: Session, base_url: str) -> None:
        """
        Initialize the reverse geocoding module.

        :param session: An instance of requests.Session for HTTP requests.
        :param base_url: The base URL for the Nominatim API.
        """
        self._session = session
        self._base_url = base_url

    @backoff.on_exception(
        backoff.expo,
        (RequestException,),
        max_tries=3,
    )
    def execute(self, lat: float, lon: float) -> dict:
        """
        Perform a reverse geocode request to Nominatim API with retry mechanism
        """
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1
        }
        response = self._session.get(f"{self._base_url}/reverse", params=params)
        response.raise_for_status()
        if not response.json():
            raise RequestException(f"No results found for coordinates lat={lat}, lon={lon}")
        return response.json()
