from dotenv import load_dotenv
from src.infra.geocoding.api import NominatimGeocodingAPI
from src.infra.logger.logger_default import LoggerDefault

# Load environment variables
load_dotenv()
if __name__ == "__main__":

    # Initialize the logger
    logger = LoggerDefault()

    # Use the NominatimGeocodingAPI with a context manager
    with NominatimGeocodingAPI(logger) as geocoding_api:
        # Example: Geocoding by address
        address = "tokopedia"
        print("Fetching geocode by address...")
        try:
            geocode_data: dict = geocoding_api.execute_geocode_by_address(address)
            # Extract and display key details
            print("Place ID:", geocode_data.get('place_id'))
            print("Name:", geocode_data.get('name'))
            print("Display Name:", geocode_data.get('display_name'))
            print("Latitude:", geocode_data.get('lat'))
            print("Longitude:", geocode_data.get('lon'))
            print("Type:", geocode_data.get('type'))
            
            address: dict = geocode_data.get('address', {})
            print("Address:")
            print("  Building:", address.get('building'))
            print("  House Number:", address.get('house_number'))
            print("  Road:", address.get('road'))
            print("  City:", address.get('city'))
            print("  County:", address.get('county'))
            print("  State:", address.get('state'))
            print("  Postcode:", address.get('postcode'))
            print("  Country:", address.get('country'))
            print("Bounding Box:", geocode_data.get('boundingbox'))
        except Exception as e:
            print(f"Failed to fetch geocode by address: {e}")

        # Example: Reverse geocoding
        latitude = -6.175392
        longitude = 106.827153
        print("\nFetching reverse geocode...")
        try:
            reverse_geocode_data: dict = geocoding_api.execute_reverse_geocode(latitude, longitude)
            # Extract and display key details
            print("Place ID:", reverse_geocode_data.get('place_id'))
            print("Name:", reverse_geocode_data.get('name'))
            print("Display Name:", reverse_geocode_data.get('display_name'))
            print("Latitude:", reverse_geocode_data.get('lat'))
            print("Longitude:", reverse_geocode_data.get('lon'))
            print("Type:", reverse_geocode_data.get('type'))

            address: dict = reverse_geocode_data.get('address', {})
            print("Address:")
            print("  Historic:", address.get('historic'))
            print("  Road:", address.get('road'))
            print("  Neighbourhood:", address.get('neighbourhood'))
            print("  City:", address.get('city'))
            print("  Region:", address.get('region'))
            print("  Postcode:", address.get('postcode'))
            print("  Country:", address.get('country'))
            print("Bounding Box:", reverse_geocode_data.get('boundingbox'))
        except Exception as e:
            print(f"Failed to fetch reverse geocode: {e}")