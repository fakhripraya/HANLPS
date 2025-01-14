from dotenv import load_dotenv
from src.infra.searchNGX.api import SearchXNG
from src.interactor.interfaces.logger.logger import LoggerInterface

# Load environment variables
load_dotenv()


class SimpleLogger(LoggerInterface):
    def log_debug(self, message: str) -> None:
        print(f"[DEBUG]: {message}")

    def log_info(self, message: str) -> None:
        print(f"[INFO]: {message}")

    def log_warning(self, message: str) -> None:
        print(f"[WARNING]: {message}")

    def log_error(self, message: str) -> None:
        print(f"[ERROR]: {message}")

    def log_critical(self, message: str) -> None:
        print(f"[CRITICAL]: {message}")

    def log_exception(self, message: str) -> None:
        print(f"[EXCEPTION]: {message}")


# Initialize the logger
logger = SimpleLogger()

# Using the SearchXNGAPI
with SearchXNG(logger) as client:
    try:
        # General search
        results = client.execute_query("laptops", filters={"category": "electronics", "price": "<1000"})
        print("Search Results:", results)
        
        # Fetch items by category
        books = client.fetch_items_by_category("books", page=1, limit=5)
        print("Books:", books)
        
        # Fetch item details
        item_details = client.fetch_item_details("item12345")
        print("Item Details:", item_details)
        
        # Fetch top-rated items
        top_rated = client.fetch_top_rated_items(category="electronics", limit=3)
        print("Top Rated Electronics:", top_rated)

        # Search for nearby restaurants
        results = client.search_places("restaurant", lat=40.7128, lon=-74.0060, radius=1000)
        print("Search Results:", results)

        # Fetch details for a specific place
        place_id = "example_place_id"
        details = client.fetch_place_details(place_id)
        print("Place Details:", details)

    except Exception as e:
        logger.log_exception(f"An error occurred during API usage: {e}")
