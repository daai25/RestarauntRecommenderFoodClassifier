import json

def load_cuisine_types(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def normalize_cuisine_types(cuisines):
    normalized = []
    for cuisine in cuisines:
        if cuisine.lower() == 'regional':
            normalized.append('swiss')
        else:
            normalized.append(cuisine.lower())
    return normalized

def main():
    cuisine_types = load_cuisine_types('cuisine_types.txt')

    with open('restaurants_compact.json', 'r', encoding='utf-8') as f:
        restaurants = json.load(f)
    print(f"Reading json with {len(restaurants)} restaurants.")

    filtered_restaurants = []
    for restaurant in restaurants:
        cuisines = restaurant.get('cuisine', [])
        normalized = normalize_cuisine_types(cuisines)
        if any(cuisine in cuisine_types for cuisine in normalized):
            restaurant['cuisine'] = normalized
            filtered_restaurants.append(restaurant)

    print(f"Restaurants left after filtering: {len(filtered_restaurants)}")

    with open('restaurants_filtered.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_restaurants, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()