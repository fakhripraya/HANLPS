""" Module provides a geocoding API interface.
"""

from abc import ABC, abstractmethod

class GeocodingAPIInterface(ABC):
    """ GeocodingAPIInterface class provides an interface for geocoding API.
    """

    @abstractmethod
    def execute_geocode_by_address(self, address: str) -> str:
        """ 
        Execute geocode method by address
        """
        
    @abstractmethod
    def execute_reverse_geocode(self, lat: str, long: str) -> str:
        """ 
        Execute reverse geocode method
        """