import json

input_file = "restaurants_Switzerland.json"
output_file = "statistics.txt"

# Load data
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

elements = data.get("elements", [])

# Counters
counts = {
    "restaurant": 0,
    "fast_food": 0,
    "cafe": 0,
    "with_url": 0,
    "with_cuisine": 0,
    "with_url_and_cuisine": 0
}

# Count
for el in elements:
    tags = el.get("tags", {})
    amenity = tags.get("amenity", "")

    if amenity == "restaurant":
        counts["restaurant"] += 1
    elif amenity == "fast_food":
        counts["fast_food"] += 1
    elif amenity == "cafe":
        counts["cafe"] += 1

    if "url" in tags or "website" in tags:
        counts["with_url"] += 1
        if "cuisine" in tags:
            counts["with_cuisine"] += 1
            counts["with_url_and_cuisine"] += 1
    elif "cuisine" in tags:
        counts["with_cuisine"] += 1

# Total
total = counts["restaurant"] + counts["fast_food"] + counts["cafe"]

# Percentages
url_pct = (counts["with_url"] / total * 100) if total else 0
cuisine_pct = (counts["with_cuisine"] / total * 100) if total else 0
url_and_cuisine_pct = (counts["with_url_and_cuisine"] / total * 100) if total else 0

# Output
report = f"""\
Restaurant Statistics – restaurants_Switzerland.json

Total gathered: {total}
- Restaurants: {counts["restaurant"]}
- Fast food: {counts["fast_food"]}
- Cafes: {counts["cafe"]}

Additional information:
- With URL: {counts["with_url"]} ({url_pct:.2f}%)
- With cuisine type: {counts["with_cuisine"]} ({cuisine_pct:.2f}%)
- With URL and cuisine type: {counts["with_url_and_cuisine"]} ({url_and_cuisine_pct:.2f}%)
"""

with open(output_file, "w", encoding="utf-8") as f:
    f.write(report)

print("Statistics written to", output_file)