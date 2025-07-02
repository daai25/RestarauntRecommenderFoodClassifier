import os
import json

if __name__ == "__main__":
    input_dir = "cantons"
    output_file = "restaurants_Switzerland.json"

    combined = {
        "version": 0.6,
        "generator": "overpass-combiner",
        "elements": []
    }

    # load all JSON files from the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            path = os.path.join(input_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "elements" in data:
                    combined["elements"].extend(data["elements"])
                else:
                    print(f"WARNING: {filename} does not contain 'elements' key, skipping.")

    # optional: delete duplicates based on type and id
    unique_elements = {}
    for el in combined["elements"]:
        key = (el["type"], el["id"])
        unique_elements[key] = el  # overwrite duplicates

    combined["elements"] = list(unique_elements.values())

    #save the combined data to a new JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"Combined data saved to {output_file}.")