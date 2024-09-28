""" This module is responsible for all reverse geocoding method.
"""

class ReverseGeocodeModules():
    """ This class is responsible for reverse geocoding method
    """

    def __init__(
            self,
            client,
    ):
        self._client = client

    def execute(
            self,
            lat: str,
            long: str
    ):
        """ This method is to reverse geocode with the given geo datas.
        :param lat: The input latitude.
        :param long: The input longitude.
        :type lat: str
        :type long: str
        :return: str
        """
        result = self.client.reverse_geocode((lat, long), enable_address_descriptor=True)
        return result
