""" Module for GeocodingAPI
"""

import requests
import googlemaps
import traceback
from configs.config import GOOGLE_MAPS_API_KEY
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.geocoding.api import GeocodingAPIInterface
from src.infra.geocoding.geocode.geocode import GeocodeModules, OSMGeocodeModules
from src.infra.geocoding.reverse_geocode.reverse_geocode import ReverseGeocodeModules, OSMReverseGeocodeModules


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
        if exc_type is not None:
            self._logger.log_exception(f"[{exc_type}]: {exc_val}")
            self._logger.log_exception(f"Traceback: {traceback.format_tb(exc_tb)}")

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

class NominatimGeocodingAPI(GeocodingAPIInterface):
    """
    Implementation of the GeocodingAPIInterface using OSM Nominatim API
    """

    BASE_URL = "https://nominatim.openstreetmap.org"

    def __init__(self, logger: LoggerInterface) -> None:
        try:
            self._logger = logger
            self._logger.log_info("Initializing Nominatim Geocoding API")
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": "Pintrail/1.0 (pintrail@gmail.com)"  # Replace with your app details
            })
        except Exception as e:
            self._logger.log_critical(f"Failed to initialize Nominatim API, ERROR: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._logger.log_exception(f"[{exc_type}]: {exc_val}")
            self._logger.log_exception(f"Traceback: {traceback.format_tb(exc_tb)}")
        self._session.close()

    def execute_geocode_by_address(self, address: str) -> str:
        """
        Execute geocode method by address using Nominatim API
        """
        try:
            module = OSMGeocodeModules(self._session, self.BASE_URL)
            data = module.execute(address)
            return data
        except Exception as e:
            self._logger.log_exception(f"Geocoding failed for address '{address}', ERROR: {e}")
            return {"error": str(e)}

    def execute_reverse_geocode(self, lat: float, lon: float) -> str:
        """
        Execute reverse geocode method using Nominatim API
        """
        try:
            module = OSMReverseGeocodeModules(self._session, self.BASE_URL)
            data = module.execute(lat, lon)
            return data
        except Exception as e:
            self._logger.log_exception(f"Reverse geocoding failed for lat={lat}, lon={lon}, ERROR: {e}")
            return {"error": str(e)}
