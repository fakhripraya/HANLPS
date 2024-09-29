""" Module for GeocodingAPI
"""
import googlemaps
from configs.config import (
    GOOGLE_MAPS_API_KEY
)
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.geocoding.api import GeocodingAPIInterface
from src.infra.geocoding.geocode.geocode import GeocodeModules
from src.infra.geocoding.reverse_geocode.reverse_geocode import ReverseGeocodeModules

class GeocodingAPI(GeocodingAPIInterface):
    
    def __init__(self, logger: LoggerInterface) -> None:
        try:
            self._logger = logger
            self._logger.log_info("Initializing google maps client")
            self._client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        except Exception as e:
            self._logger.log_critical(f"Failed to start maps client, ERROR: {e}")
            
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Exiting Type:{exc_type}")
        print(f"Exiting Val :{exc_val}")
        print(f"Exiting TB :{exc_tb}")
        
    def execute_geocode_by_address(self, address) -> str:
        """ 
        Execute geocode method by address
        """
        module = GeocodeModules(self._client)
        data = module.execute(address)
        return data
        
    def execute_reverse_geocode(self, lat, long) -> str:
        """ 
        Execute reverse geocode method
        """
        module = ReverseGeocodeModules(self._client)
        data = module.execute(lat, long)
        return data