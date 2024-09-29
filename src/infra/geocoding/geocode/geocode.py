""" This module is responsible for all geocoding method.
"""
from googlemaps import Client, geocoding

class GeocodeModules():
    """ This class is responsible for geocoding method
    """

    def __init__(
            self,
            client: Client,
    ):
        self._client = client
        
    def execute(
            self,
            address: str,
    ):
        """ This method is to geocode with the given address.
        :param address: The input address.
        :type address: str
        :return: str
        """
        result = geocoding.geocode(self._client, address)
        return result
