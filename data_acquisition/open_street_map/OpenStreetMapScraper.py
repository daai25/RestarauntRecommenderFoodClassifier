# OpenStreetMap Scraper for Restaurants in Swiss Cantons
# Please do not run this script, if not necessary

import requests
import json
import time
import os
import random
import re

# Template to gather all the restaurants, fast food and cafés in each canton
std_template = """
[out:json][timeout:180];
area["name"="{name}"]["boundary"="administrative"]["admin_level"="4"]->.a;
(
  node["amenity"="restaurant"](area.a);
  node["amenity"="cafe"](area.a);
  node["amenity"="fast_food"](area.a);
);
out center;
"""

def get_regions(region_list_file: str) -> list:
    """
    Reads a list of regions from a file and returns them as a list.
    The containing regions names must be a valid admin level 4 region on the OpenStreetMap.

    @param region_list_file: Path to the file containing the list of regions.
    @return: A list of regions inside the file.
    """
    with open(region_list_file, "r", encoding="utf-8") as f:
        regions = [line.strip() for line in f if line.strip()]
    return regions

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

def normalize_cuisine_types(cuisines):
    """
    Normalize cuisine types by replacing 'regional' with 'swiss'.
    """
    normalized = []
    for cuisine in cuisines:
        if cuisine == 'regional':
            normalized.append('swiss')
        else:
            normalized.append(cuisine)
    return normalized


class OpenStreetMapScraper:
    def __init__(self, template: str, region_list_file: str, output_dir: str):
        # Check if the region list file exists
        if not os.path.exists(region_list_file):
            raise FileNotFoundError(f"Region list file '{region_list_file}' does not exist.")

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        self.template = template
        self.regions = get_regions(region_list_file)

        # set up output directories
        self.output_dir = output_dir
        self.output_raw_data_dir = os.path.join(output_dir, "raw_data")
        self.output_region_dir = os.path.join(output_dir, "raw_data", "regions")
        self.output_statistics_dir = os.path.join(output_dir, "raw_data", "statistics")
        # Creating the output directory structure
        self.setup_output_directory()

        # define json file paths
        self.combined_json_file = os.path.join(self.output_raw_data_dir, "restaurants.json")
        self.combined_stat_file = os.path.join(self.output_statistics_dir, "restaurants_stats.txt")
        self.combined_cleaned_json_file = os.path.join(self.output_raw_data_dir, "restaurants_clean.json")
        self.filtered_json_file = os.path.join(self.output_raw_data_dir, "restaurants_filtered.json")
        self.filtered_stat_file = os.path.join(self.output_statistics_dir, "restaurants_filtered_stats.txt")

    def setup_output_directory(self):
        """
        Creates the following directory structure:
        - output_dir
            - raw_data
                - regions
                - statistics
        """
        os.makedirs(self.output_region_dir, exist_ok=True)
        os.makedirs(self.output_statistics_dir, exist_ok=True)

    def get_restaurant_json(self):
        """
        Fetches restaurant data for each region defined in the region list file.
        Saves the data as JSON files in the output directory.
        """
        for region in self.regions:
            region_str = region.replace(' ', '_').replace('/', '_').replace('.', '').lower()

            filename = os.path.join(self.output_dir, "raw_data", "regions", f"{region_str}.json")
            if os.path.exists(filename):
                print(f"Skipping {region}, file already exists.")
                continue

            print(f"Gathering restaurants in {region} ...")
            query = self.template.format(name=region)
            response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})

            if response.ok:
                with open(filename, "w", encoding="utf-8") as file:
                    json.dump(response.json(), file, ensure_ascii=False, indent=2)
            else:
                print(f"Error with {region}: {response.status_code}")

            time_to_sleep = random.randint(1, 10)
            print(f"Waiting for {time_to_sleep} seconds before next request...")
            time.sleep(time_to_sleep)

        print("Finished gathering restaurant data for all regions.")

    def combine_region_json(self, generate_statistics: bool = False):
        combined = {
            "version": 0.6,
            "generator": "overpass-combiner",
            "elements": []
        }

        # load all JSON files from the output_region_dir
        for filename in os.listdir(self.output_region_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.output_region_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "elements" in data:
                        combined["elements"].extend(data["elements"])
                    else:
                        print(f"{filename} does not contain 'elements' key, skipping.")

        # optional: delete duplicates based on type and id
        unique_elements = {}
        for el in combined["elements"]:
            key = (el["type"], el["id"])
            unique_elements[key] = el  # overwrite duplicates

        combined["elements"] = list(unique_elements.values())

        # save the combined data to a new JSON file
        with open(self.combined_json_file, "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)

        print(f"Combined JSON file saved to {self.combined_json_file}")

        if generate_statistics:
            counts = {
                "restaurant": 0,
                "fast_food": 0,
                "cafe": 0,
                "with_url": 0,
                "with_cuisine": 0,
                "with_url_and_cuisine": 0
            }

            for el in combined["elements"]:
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

            total = counts["restaurant"] + counts["fast_food"] + counts["cafe"]

            url_pct = (counts["with_url"] / total * 100) if total else 0
            cuisine_pct = (counts["with_cuisine"] / total * 100) if total else 0
            url_and_cuisine_pct = (counts["with_url_and_cuisine"] / total * 100) if total else 0

            report = f"""
            Restaurant Statistics – restaurants.json

            Total gathered: {total}
            - Restaurants: {counts["restaurant"]}
            - Fast food: {counts["fast_food"]}
            - Cafes: {counts["cafe"]}

            Additional information:
            - With URL: {counts["with_url"]} ({url_pct:.2f}%)
            - With cuisine type: {counts["with_cuisine"]} ({cuisine_pct:.2f}%)
            - With URL and cuisine type: {counts["with_url_and_cuisine"]} ({url_and_cuisine_pct:.2f}%)
            """

            with open(self.combined_stat_file, "w", encoding="utf-8") as f:
                f.write(report)

            print(f"Statistics written to {self.combined_stat_file}")

    def cleanup_json(self, desired_tags: list):
        with open(self.combined_json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        elements = data.get('elements', [])

        cleaned_elements = []
        for el in elements:
            compact = {
                'id': el.get('id'),
                'lat': el.get('lat'),
                'lon': el.get('lon'),
            }

            tags = el.get('tags', {})
            for tag in desired_tags:
                if tag in tags:
                    if tag == 'cuisine':
                        # special exception for 'cuisine'
                        compact[tag] = clean_cuisine_type(tags[tag])
                    else:
                        compact[tag] = tags[tag]

            cleaned_elements.append(compact)

        # save the cleaned data to a new JSON file
        with open(self.combined_cleaned_json_file, "w", encoding="utf-8") as f:
            json.dump(cleaned_elements, f, ensure_ascii=False, indent=2)

        print(f"Cleaned JSON file saved to {self.combined_cleaned_json_file}")

    def filter_cuisine_types(self, cuisine_type_file, generate_statistics: bool = False):
        with open(cuisine_type_file, 'r', encoding='utf-8') as f:
            cuisine_types = set(line.strip() for line in f if line.strip())

        with open(self.combined_cleaned_json_file, 'r', encoding='utf-8') as f:
            restaurants = json.load(f)

        filtered_restaurants = []
        for restaurant in restaurants:
            cuisines = restaurant.get('cuisine', [])
            normalized = normalize_cuisine_types(cuisines)
            if any(cuisine in cuisine_types for cuisine in normalized):
                restaurant['cuisine'] = normalized
                filtered_restaurants.append(restaurant)

        with open(self.filtered_json_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_restaurants, f, ensure_ascii=False, indent=2)

        print(f"Filtered restaurants saved to {self.filtered_json_file}")

        if generate_statistics:
            total_restaurants = len(restaurants)
            filtered_count = len(filtered_restaurants)
            filter_pct = (filtered_count / total_restaurants * 100) if total_restaurants else 0

            # count the number of restaurants have a website or cuisine type
            with_url = sum(1 for r in filtered_restaurants if 'url' in r or 'website' in r)
            with_url_pct = (with_url / filtered_count * 100) if filtered_count else 0

            report = f"""
            Filtered Restaurant Statistics – restaurants_filtered.json

            Total restaurants before filtering: {total_restaurants}
            Total restaurants after filtering: {filtered_count}
            Filtered percentage: {filter_pct:.2f}%
            
            Total of restaurants with URL or website: {with_url}
            Percentages of restaurants with URL or website: {with_url_pct:.2f}%
            """

            with open(self.filtered_stat_file, "w", encoding="utf-8") as f:
                f.write(report)

            print(f"Filtered statistics written to {self.filtered_stat_file}")



if __name__ == "__main__":
    # Read in the OpenStreetMap region list, which we want to get
    osm_scraper = OpenStreetMapScraper(
        template=std_template,
        region_list_file="list_of_regions.txt",
        output_dir="output"
    )

    # get the restaurant data for each region
    osm_scraper.get_restaurant_json()
    # combine the region JSON files into one
    osm_scraper.combine_region_json(generate_statistics=True)
    # cleanup the combined JSON file
    osm_scraper.cleanup_json(['name', 'addr:city', 'cuisine', 'website', 'url'])
    # filter out restaurants with invalid cuisine types
    osm_scraper.filter_cuisine_types("cuisine_types.txt", generate_statistics=True)

