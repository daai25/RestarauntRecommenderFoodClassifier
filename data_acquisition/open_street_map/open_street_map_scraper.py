# OpenStreetMap Scraper for Restaurants in Swiss Cantons
# Please do not run this script, if not necessary

import requests
import json
import time
import os
import random

kantone = [
    "Aargau", "Appenzell Ausserrhoden", "Appenzell Innerrhoden", "Basel-Landschaft",
    "Basel-Stadt", "Bern/Berne", "Fribourg/Freiburg", "Genève", "Glarus", "Graubünden/Grischun/Grigioni", "Jura", "Luzern",
    "Neuchâtel", "Nidwalden", "Obwalden", "Schaffhausen", "Schwyz", "Solothurn",
    "St. Gallen", "Ticino", "Thurgau", "Uri", "Vaud", "Valais/Wallis", "Zug", "Zürich"
]

# Template to gather all the restaurants, fast food and cafés in each canton in Switzerland
template = """
[out:json][timeout:180];
area["name"="{name}"]["boundary"="administrative"]["admin_level"="4"]->.a;
(
  node["amenity"="restaurant"](area.a);
  node["amenity"="cafe"](area.a);
  node["amenity"="fast_food"](area.a);
);
out center;
"""

if __name__ == "__main__":
    # Ensure the output directory exists
    os.makedirs("raw_data/cantons", exist_ok=True)

    for k in kantone:
        filename = f"raw_data/cantons/restaurants_{k.replace(' ', '_').replace('/', '_')}.json"
        if os.path.exists(filename):
            print(f"Skipping {k}, file already exists.")
            continue

        print(f"Gathering restaurants in {k} ...")
        query = template.format(name=k)
        response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
        if response.ok:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=2)
        else:
            print(f"Error with {k}: {response.status_code}")

        time_to_sleep = random.randint(1, 20)
        print(f"Waiting for {time_to_sleep} seconds before next request...")
        time.sleep(time_to_sleep)