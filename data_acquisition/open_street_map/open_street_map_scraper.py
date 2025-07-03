# OpenStreetMap Scraper for Restaurants in Swiss Cantons
# Please do not run this script, if not necessary

import requests
import json
import time
import os
import random

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


class OpenStreetMapScraper:
    def __init__(self, template: str, region_list_file: str, output_dir: str):
        # Check if the region list file exists
        if not os.path.exists(region_list_file):
            raise FileNotFoundError(f"Region list file '{region_list_file}' does not exist.")

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        self.template = template
        self.output_dir = output_dir
        self.regions = get_regions(region_list_file)

        # Creating the output directory structure
        self.setup_output_directory()

    def setup_output_directory(self):
        """
        Creates the following directory structure:
        - output_dir
            - raw_data
                - regions
                - statistics
        """
        os.makedirs(os.path.join(self.output_dir, "raw_data", "regions"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "raw_data", "statistics"), exist_ok=True)

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


if __name__ == "__main__":
    # Read in the OpenStreetMap region list, which we want to get
    osm_scraper = OpenStreetMapScraper(
        template=std_template,
        region_list_file="list_of_regions.txt",
        output_dir="output"
    )

