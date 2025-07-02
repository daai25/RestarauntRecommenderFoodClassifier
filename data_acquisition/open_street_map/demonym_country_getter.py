import json
import requests
import os

def get_demonym(country_name):
    try:
        response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}")
        data = response.json()
        # include small random delay
        return data[0]["demonyms"]["eng"]["m"]
    except Exception as e:
        print(f"Error fetching demonym for {country_name}: {e}")
        return "Unknown"

if __name__ == "__main__":
    input_file = "all_osm_countries.json"
    output_file = "cuisine_types.txt"

    # if the output file was already created, do not run the script again
    if os.path.exists(output_file):
        print(f"{output_file} already exists. Skipping the script.")
        exit()

    # load the JSON data
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # extract the english country names
    # include only country's with tag "type": "boundary"
    countries = []
    for country in data.get("elements", []):
        if "tags" in country and "name:en" in country["tags"]:
            if country["tags"]["type"] == "boundary":
                countries.append(country["tags"]["name:en"])

    print(f"Finished extracting {len(countries)} countries from the data.")
    # remove duplicates and sort the list
    countries = sorted(set(countries))

    # get the demonym for each country
    countries_demonyms = [get_demonym(country) for country in countries]
    print(f"Finished fetching demonyms for {len(countries_demonyms)} countries.")

    # remove duiplicates
    countries_demonyms = list(set(countries_demonyms))

    # remove the "Unkown" demonym
    countries_demonyms = [d for d in countries_demonyms if d != "Unknown"]

    # split the demonyms by comma
    for cd in countries_demonyms:
        if "," in cd:
            parts = cd.split(",")
            countries_demonyms.remove(cd)
            countries_demonyms.extend([part.strip() for part in parts if part.strip()])

    # normalize the demonyms
    countries_demonyms = [d.replace(" ", "_").lower() for d in countries_demonyms]

    # sort the demonyms
    countries_demonyms = sorted(countries_demonyms)

    # write demonyms to a file
    with open(output_file, "w", encoding="utf-8") as f:
        for demonym in countries_demonyms:
            f.write(f"{demonym}\n")