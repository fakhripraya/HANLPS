""" This module is responsible for all reverse geocoding method.
"""

import backoff
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
