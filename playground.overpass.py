# Import the OverpassAPI class and any required dependencies
from src.infra.geocoding.overpass.api import OverpassAPI
from src.interactor.interfaces.logger.logger import LoggerInterface

class SimpleLogger(LoggerInterface):
    """
    A simple implementation of LoggerInterface for testing.
    """

    def log_info(self, message: str) -> None:
        print(f"[INFO]: {message}")
    
    def log_debug(self, message: str) -> None:
        print(f"[DEBUG]: {message}")

    def log_warning(self, message: str) -> None:
        print(f"[WARNING]: {message}")

    def log_error(self, message: str) -> None:
        print(f"[ERROR]: {message}")

    def log_exception(self, message: str) -> None:
        print(f"[EXCEPTION]: {message}")

    def log_critical(self, message: str) -> None:
        print(f"[CRITICAL]: {message}")


if __name__ == "__main__":
    # Initialize the logger
    logger = SimpleLogger()

    # Use the OverpassAPI with a context manager
    with OverpassAPI(logger) as overpass_api:
        # Example: Fetch restaurants near a given location
        latitude = 52.5200  # Latitude for Berlin, Germany
        longitude = 13.4050  # Longitude for Berlin, Germany
        search_radius = 1000  # Radius in meters
        amenity_type = "restaurant"  # Amenity type to search for

        print("Fetching POIs by amenity...")
        try:
            pois = overpass_api.fetch_pois_by_amenity(latitude, longitude, search_radius, amenity_type)
            print("POIs found:", pois)
        except Exception as e:
            print(f"Failed to fetch POIs by amenity: {e}")

        # Example: Fetch points of interest by category
        category_type = "tourism"  # Category to search for
        print("\nFetching POIs by category...")
        try:
            pois_by_category = overpass_api.fetch_pois_by_category(latitude, longitude, search_radius, category_type)
            print("POIs found by category:", pois_by_category)
        except Exception as e:
            print(f"Failed to fetch POIs by category: {e}")
