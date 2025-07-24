import requests
import time
import csv

API_KEY = 'AIzaSyCRdL4t6Ldd0Pjm6bFRjBWa_v3cChvBI3Y'
CITY = 'Winterthur'
INPUT_FILE = 'restaurant_list.txt'
OUTPUT_FILE = 'google_reviews.csv'

def find_place_id(restaurant_name):
    """
    Given a restaurant name, fetches the restaurant's Google Maps ID.

    @param restaurant_name: Name of restaurant from restaurant list.
    @return: Restaurant ID from the top search result, or none if not found.
    """

    # Format search request
    query = f"{restaurant_name}, {CITY}"
    url = (
        "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        f"?input={requests.utils.quote(query)}"
        f"&inputtype=textquery"
        f"&fields=place_id"
        f"&key={API_KEY}"
    )
    response = requests.get(url).json()
    candidates = response.get("candidates")

    # Check for results
    if candidates:
        return candidates[0]["place_id"]
    return None

def get_reviews(place_id):
    """
    Given the restaurant ID, fetches top 5 reviews.

    @param place_id: Restaurant Google Maps ID.
    @return: List of top 5 most relevant reviews, or empty list if no reviews found.
    """

    # Format reviews request
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}"
        f"&fields=name,reviews"
        f"&key={API_KEY}"
    )
    response = requests.get(url).json()
    result = response.get("result", {})

    # Return empty list if no reviews
    return result.get("reviews", [])

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile, open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='|')
        
        # Fetch each restaurant from restaurant list and ensure not NULL
        for line in infile:
            restaurant = line.strip()
            if not restaurant:
                continue

            # Fetch restaurant ID and ensure not NULL
            place_id = find_place_id(restaurant)
            if not place_id:
                print(f"Not found: {restaurant}")
                continue

            # Fetch reviews and grab relevant data for output
            reviews = get_reviews(place_id)
            for review in reviews:
                author = review.get("author_name", "NA")
                rating = review.get("rating", "NA")
                timestamp = review.get("time", 0)
                date = time.strftime('%Y-%m-%d', time.localtime(timestamp))
                
                # Skip review if author or rating missing
                if author == "NA" or rating == "NA":
                    continue
                writer.writerow([restaurant, author.replace(",", ""), rating, date])
            time.sleep(0.1)  # Respect rate limits

if __name__ == '__main__':
    main()
