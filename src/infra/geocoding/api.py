""" Module for GeocodingAPI
"""
from configs.config import (
    GOOGLE_MAPS_API_KEY
)
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.geocoding.api import GeocodingAPIInterface

class GeocodingAPI(GeocodingAPIInterface):
    
    def __init__(self, logger: LoggerInterface) -> None: 
        self._api_key = GOOGLE_MAPS_API_KEY
        self._logger = logger
        
    def execute_geocode_by_address(self, address: str) -> str:
        """ 
        Execute geocode method by address
        """
        
    def execute_reverse_geocode(self, lat: str, long: str) -> str:
        """ 
        Execute reverse geocode method
        """