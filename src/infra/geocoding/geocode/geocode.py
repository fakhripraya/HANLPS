""" This module is responsible for all geocoding method.
"""

class GeocodeModules():
    """ This class is responsible for geocoding method
    """

    def __init__(
            self,
            client,
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
        result = self.client.geocode(address)
        return result
