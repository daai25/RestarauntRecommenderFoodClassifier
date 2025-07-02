# OpenStreetMap Scraper for Restaurants in Swiss Cantons
# Please do not run this script, if not necessary

import requests
import json
import time

kantone = [
    "Aargau", "Appenzell Ausserrhoden", "Appenzell Innerrhoden", "Basel-Landschaft",
    "Basel-Stadt", "Bern", "Freiburg", "Genf", "Glarus", "Graubünden", "Jura", "Luzern",
    "Neuenburg", "Nidwalden", "Obwalden", "Schaffhausen", "Schwyz", "Solothurn",
    "St. Gallen", "Tessin", "Thurgau", "Uri", "Waadt", "Wallis", "Zug", "Zürich"
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

for k in kantone:
    print(f"Gather Restaurants in {k} ...")
    query = template.format(name=k)
    response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
    if response.ok:
        with open(f"raw_data/cantons/restaurants_{k.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)
    else:
        print(f"Error with {k}: {response.status_code}")
    time.sleep(10)  # small delay to avoid overloading the server