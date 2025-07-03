import json
import os

from raw_data.cuisine_type_extractor import clean_cuisine_type

INPUT_FILE = 'raw_data/restaurants_Switzerland.json'
OUTPUT_DIR = '.'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'restaurants_compact.json')

# Liste der gewünschten Tags
DESIRED_TAGS = ['name', 'addr:city', 'cuisine', 'website']


def extract_relevant_data(element):
    # Basisdaten
    compact = {
        'id': element.get('id'),
        'lat': element.get('lat'),
        'lon': element.get('lon'),
    }

    # Tags extrahieren
    tags = element.get('tags', {})
    for tag in DESIRED_TAGS:
        if tag in tags:
            if tag == 'cuisine':
                # special exception for 'cuisine'
                compact[tag] = clean_cuisine_type(tags[tag])
            else:
                compact[tag] = tags[tag]

    return compact


def main():
    # Input-Datei laden
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    elements = data.get('elements', [])

    # Relevante Felder extrahieren
    compact_data = [extract_relevant_data(el) for el in elements]

    # Zielordner erstellen
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Kompaktes JSON schreiben
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(compact_data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
