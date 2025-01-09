""" This module is responsible for all geocoding method.
"""

import backoff
from requests import Session
from requests.exceptions import RequestException
from googlemaps import Client, geocoding
from googlemaps.exceptions import ApiError, TransportError, Timeout


class GeocodeModules:
    """This class is responsible for geocoding method"""

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
    def execute(
        self,
        address: str,
    ):
        """This method is to geocode with the given address.
        :param address: The input address.
        :type address: str
        :return: str
        """
        result = geocoding.geocode(
            self._client,
            address,
        )
        return result
    
class OSMGeocodeModules:
    """This class is responsible for geocoding method using OSM"""

    def __init__(self, session: Session, base_url: str) -> None:
        """
        Initialize the geocoding module.

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
    def execute(self, address: str) -> dict:
        """
        Perform a geocode request to Nominatim API with retry mechanism
        """
        params = {
            "q": address,
            "format": "json",
            "addressdetails": 1,
            "limit": 1
        }
        response = self._session.get(f"{self._base_url}/search", params=params)
        response.raise_for_status()
        if not response.json():
            raise RequestException(f"No results found for address '{address}'")
        return response.json()[0]

