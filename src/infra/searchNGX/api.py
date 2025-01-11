import requests
import backoff
from requests.exceptions import RequestException
from src.interactor.interfaces.logger.logger import LoggerInterface


class SearchXNG:
    """
    This class integrates with the SearchXNG API to perform advanced searches and fetch results.
    """

    BASE_URL = "https://searchxng-api.example.com/v1"

    def __init__(self, logger: LoggerInterface) -> None:
        """
        Initialize the SearchXNG client.
        :param logger: LoggerInterface instance for logging
        """
        try:
            self._logger = logger
            self._logger.log_info("Initializing SearchXNG client")
            self._session = requests.Session()
            self._session.headers.update({
                "Authorization": "Bearer YOUR_API_KEY",  # Replace with your API key
                "Content-Type": "application/json",
                "User-Agent": "YourAppName/1.0 (your_email@example.com)"  # Replace with your app details
            })
        except Exception as e:
            self._logger.log_critical(f"Failed to initialize SearchXNG client, ERROR: {e}")

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
        max_tries=5,
    )
    def _send_request(self, endpoint: str, method: str = "GET", params: dict = None, data: dict = None) -> dict:
        """
        Send a request to the SearchXNG API.
        :param endpoint: API endpoint (e.g., "/search")
        :param method: HTTP method (GET, POST, etc.)
        :param params: Query parameters for GET requests
        :param data: JSON payload for POST requests
        :return: JSON response from the API
        """
        url = f"{self.BASE_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self._session.get(url, params=params)
            elif method.upper() == "POST":
                response = self._session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._logger.log_exception(f"Request to {url} failed, ERROR: {e}")
            raise

    def execute_query(self, query: str, filters: dict = None) -> dict:
        """
        Execute a custom query on the SearchXNG API.
        :param query: Search query string
        :param filters: Additional filters for the search (e.g., {"category": "books", "price": "<100"})
        :return: JSON response from the SearchXNG API
        """
        params = {"query": query}
        if filters:
            params.update(filters)
        
        return self._send_request("/search", method="GET", params=params)

    def fetch_items_by_category(self, category: str, page: int = 1, limit: int = 10) -> dict:
        """
        Fetch items by category.
        :param category: Category to filter items (e.g., 'electronics', 'books')
        :param page: Page number for pagination
        :param limit: Number of results per page
        :return: JSON response containing items in the specified category
        """
        params = {"category": category, "page": page, "limit": limit}
        return self._send_request("/items", method="GET", params=params)

    def fetch_item_details(self, item_id: str) -> dict:
        """
        Fetch detailed information about a specific item.
        :param item_id: Unique identifier of the item
        :return: JSON response containing item details
        """
        return self._send_request(f"/items/{item_id}", method="GET")

    def fetch_top_rated_items(self, category: str = None, limit: int = 5) -> dict:
        """
        Fetch top-rated items, optionally filtered by category.
        :param category: Category to filter items (e.g., 'electronics', 'books') (optional)
        :param limit: Number of top-rated items to fetch
        :return: JSON response containing top-rated items
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        
        return self._send_request("/items/top-rated", method="GET", params=params)
