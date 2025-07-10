import requests
import time
import csv

API_KEY = 'AIzaSyCRdL4t6Ldd0Pjm6bFRjBWa_v3cChvBI3Y'
CITY = 'Winterthur'
INPUT_FILE = 'restaurant_list.txt'
OUTPUT_FILE = 'google_reviews.csv'

def find_place_id(restaurant_name):
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
    if candidates:
        return candidates[0]["place_id"]
    return None

def get_reviews(place_id):
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}"
        f"&fields=name,reviews"
        f"&key={API_KEY}"
    )
    response = requests.get(url).json()
    result = response.get("result", {})
    reviews = result.get("reviews", [])
    return result.get("name", "Unknown"), reviews

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile, open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='|')
        for line in infile:
            restaurant = line.strip()
            if not restaurant:
                continue
            place_id = find_place_id(restaurant)
            if not place_id:
                print(f"Not found: {restaurant}")
                continue
            name, reviews = get_reviews(place_id)
            for review in reviews:
                author = review.get("author_name", "UnknownUser")
                rating = review.get("rating", "")
                timestamp = review.get("time", 0)
                date = time.strftime('%Y-%m-%d', time.localtime(timestamp))
                writer.writerow([name, author, rating, date])
            time.sleep(0.1)  # Respect rate limits

if __name__ == '__main__':
    main()
