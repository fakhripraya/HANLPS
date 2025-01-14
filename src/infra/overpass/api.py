import requests
import backoff
from requests.exceptions import RequestException
from src.interactor.interfaces.logger.logger import LoggerInterface

class OverpassAPI:
    """
    This class integrates with the Overpass API to fetch OSM data such as POIs.
    """

    BASE_URL = "https://overpass-api.de/api/interpreter"

    def __init__(self, logger: LoggerInterface) -> None:
        """
        Initialize the Overpass API client.
        :param logger: LoggerInterface instance for logging
        """
        try:
            self._logger = logger
            self._logger.log_info("Initializing Overpass API client")
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": "YourAppName/1.0 (your_email@example.com)"  # Replace with your app details
            })
        except Exception as e:
            self._logger.log_critical(f"Failed to initialize Overpass API, ERROR: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._logger.log_exception(f"[{exc_type}]: {exc_val}")
            self._logger.log_exception(f"Traceback: {exc_tb}")
        self._session.close()

    @backoff.on_exception(
        backoff.expo,
        (RequestException,),
        max_tries=3,
    )
    def execute_query(self, query: str) -> dict:
        """
        Execute a custom query on the Overpass API.
        :param query: Overpass QL (query language) string
        :return: JSON response from the Overpass API
        """
        try:
            response = self._session.get(self.BASE_URL, params={"data": query})
            response.raise_for_status()
            data = response.json()
            if "elements" not in data:
                raise ValueError("Invalid Overpass API response: 'elements' missing")
            return data
        except Exception as e:
            self._logger.log_exception(f"Failed to execute Overpass query, ERROR: {e}")
            raise

    def fetch_pois_by_amenity(self, lat: float, lon: float, radius: int, amenity: str) -> dict:
        """
        Fetch Points of Interest (POIs) by amenity type within a radius.
        :param lat: Latitude of the central point
        :param lon: Longitude of the central point
        :param radius: Search radius in meters
        :param amenity: OSM amenity tag (e.g., 'restaurant', 'hospital')
        :return: JSON response containing matching POIs
        """
        query = f"""
        [out:json];
        node
          ["amenity"="{amenity}"]
          (around:{radius},{lat},{lon});
        out;
        """
        return self.execute_query(query)

    def fetch_pois_by_category(self, lat: float, lon: float, radius: int, category: str) -> dict:
        """
        Fetch Points of Interest (POIs) by category (e.g., 'tourism', 'shop').
        :param lat: Latitude of the central point
        :param lon: Longitude of the central point
        :param radius: Search radius in meters
        :param category: OSM category tag (e.g., 'tourism', 'shop')
        :return: JSON response containing matching POIs
        """
        query = f"""
        [out:json];
        node
          ["{category}"]
          (around:{radius},{lat},{lon});
        out;
        """
        return self.execute_query(query)
