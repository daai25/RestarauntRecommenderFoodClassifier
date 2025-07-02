import re
import json

with open("restaurants_Switzerland.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# prepare set for the cuisine type
cuisines = set()

for element in data.get("elements", []):
    tags = element.get("tags", {})
    cuisine = tags.get("cuisine")
    if cuisine:
        # split multiple types
        types = [c.strip() for c in re.split(r'[;&]', cuisine)]

        cleaned_types = [
            t.replace(" ", "_").replace("-", "_").lower() # clean up the types
            for t in types
            if not t.strip().lower().startswith("http") # filter out URLs
        ]
        cuisines.update(cleaned_types)

# sort alphabetically
sorted_cuisines = sorted(cuisines)

# write result into txt file
with open("cuisine_types.txt", "w", encoding="utf-8") as f:
    f.write(f"Found individual cuisine types: {len(sorted_cuisines)}\n\n")

    for cuisine in sorted_cuisines:
        f.write(cuisine + "\n")