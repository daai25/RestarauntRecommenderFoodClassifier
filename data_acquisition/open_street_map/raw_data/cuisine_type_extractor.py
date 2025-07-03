import re
import json

def clean_cuisine_type(cuisine_tag) -> list:
    """Clean and format the cuisine type."""
    # split multiple types
    type_list = [c.strip() for c in re.split(r'[;&]', cuisine_tag)]

    cleaned_type_list = [
        t.replace(" ", "_").replace("-", "_").lower()  # clean up the types
        for t in type_list
        if not t.strip().lower().startswith("http")  # filter out URLs
    ]

    return cleaned_type_list

if __name__ == "__main__":
    with open("restaurants_Switzerland.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # prepare set for the cuisine type
    cuisines = set()

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        cuisine = tags.get("cuisine")
        if cuisine:
            cuisines.update(clean_cuisine_type(cuisine))

    # sort alphabetically
    sorted_cuisines = sorted(cuisines)

    # write result into txt file
    with open("cuisine_types.txt", "w", encoding="utf-8") as f:
        f.write(f"Found individual cuisine types: {len(sorted_cuisines)}\n\n")

        for cuisine in sorted_cuisines:
            f.write(cuisine + "\n")