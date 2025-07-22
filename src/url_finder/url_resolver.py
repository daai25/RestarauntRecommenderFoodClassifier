from geopy.geocoders import Nominatim
from ddgs import DDGS
import tldextract
import logging


_AGGREGATOR_DOMAINS = {
    "tripadvisor.com",
    "yelp.com",
    "opentable.com",
    "foursquare.com",
    "google.com",
    "facebook.com",
    "zomato.com",
    "just-eat.com",
    "deliveroo.com",
    "ubereats.com",
    "doordash.com",
    "grubhub.com",
    "swiggy.com",
    "foodpanda.com",
    "wheree.com",
}


def _get_location_of_coordinates(lat: float, lon: float) -> tuple:
    """
    Get the city and country of a location based on latitude and longitude using reverse geocoding.

    Since we use the Nominatim service, only one request per second is allowed.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        tuple: A tuple containing the city and country of the location.

    """
    geolocator = Nominatim(user_agent="FoodClassifier")
    location = geolocator.reverse((lat, lon), exactly_one=True, language="en")
    if location is None:
        return None, None
    address = location.raw["address"]
    city = address.get("city") or (
        address.get("town") or address.get("village") or address.get("hamlet")
    )

    print(city)

    country = address.get("country", "")
    return city, country


def _get_url_of_coordinates_and_name(
    rest_name: str, city: str, country: str
) -> str | None:
    """
    Get the URL of a restaurant based on its name, city, and country using DuckDuckGo search.

    Args:
        rest_name (str): Name of the restaurant.
        city (str): City where the restaurant is located.
        country (str): Country where the restaurant is located.

    Returns:
        str: The URL of the restaurant if found, otherwise None.
    """
    query = f"Restaurant {rest_name} {city} {country}"
    results = DDGS().text(query, max_results=5)

    for r in results:
        url = r.get("href")
        if not url:
            continue
        domain = tldextract.extract(url).registered_domain
        if domain in _AGGREGATOR_DOMAINS:
            continue
        if url.count("/") <= 4:
            return url
    return None


def get_missing_url(rest_name: str, lat: float, lon: float) -> str | None:
    """
    Get the URL of a restaurant based on its name and coordinates (latitude and longitude).

    Args:
        rest_name (str ): Name of the restaurant.
        lat (float): Latitude of the restaurant.
        lon (float): Longitude of the restaurant.

    Returns:
        str: The URL of the restaurant if found, otherwise None.
    """
    location = _get_location_of_coordinates(lat, lon)

    potential_url = _get_url_of_coordinates_and_name(
        rest_name, location[0], location[1]
    )
    if potential_url:
        logging.info(
            "For restaurant: %s located in: %s, %s", rest_name, location[0], location[1]
        )
        logging.info("Found URL: %s", potential_url)
    else:
        logging.warning("No URL found for the restaurant.")

    return potential_url


if __name__ == "__main__":

    # Example usage
    latitude = 47.349098
    longitude = 8.3464357
    restaurant_name = "Köbis Promenade"
    pot_url = get_missing_url(restaurant_name, latitude, longitude)
    print(f"Potential URL: {pot_url}")
