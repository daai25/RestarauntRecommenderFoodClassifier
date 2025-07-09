from modelling.food_or_not_food import FoodOrNotFood

import os
import json
import pandas as pd

class FoodOrNotFoodFilter:
    def __init__(self, model_path, status_csv_fils="scrape_status.csv", device=None, verbose: bool=False):
        """
        Initializes the FoodOrNotFoodFilter with a model for classifying images as food or not food.

        Args:
            model_path (str): Path to the file with the trained model weights (.pth).
            status_csv_fils (str): Path to the CSV file that keeps track of the scraping status.
            device (str, optional): Device to use ('cuda', 'cpu'). If not specified, selected automatically.
            verbose (bool, optional): If True, prints information about the scraping status.

        Raises:
            FileNotFoundError: If the specified model file or status CSV file does not exist.
        """
        self.model = FoodOrNotFood.FoodOrNotFood(model_path=model_path, device=device)

        if not os.path.exists(status_csv_fils):
            raise FileNotFoundError(f"Status CSV file not found: {status_csv_fils}")
        self.status_csv_file = status_csv_fils
        self.status_df = pd.read_csv(self.status_csv_file, dtype={'id': str})

        self.verbose = verbose

    def filter_images(self, image_dir) -> tuple[int, int]:
        """
        Filters images in the specified directory to keep only those classified as food.

        Args:
            image_dir (str): Path to the directory containing images to filter.

        Returns:
            tuple: A tuple containing:
                - int: Count of images classified as food.
                - int: Count of images that were removed (not classified as food).
        """
        # Checks if the image directory exists
        if not os.path.exists(image_dir):
            raise FileNotFoundError(f"Image directory not found: {image_dir}")
        # Check if the directory is not empty
        if not os.listdir(image_dir):
            raise ValueError(f"Image directory is empty: {image_dir}")

        # Get the restaurant id from the image directory name
        # The format of the dir should be "some/path/restaurant_id/images"
        parts = image_dir.strip(os.sep).split(os.sep)
        restaurant_id = parts[-2] if len(parts) >= 2 else None
        if not restaurant_id:
            raise ValueError(f"Could not extract restaurant ID from path: {image_dir}")

        if restaurant_id not in self.status_df['id'].values:
            # If not, add a new row with initial status
            # TODO: Make a CSV Writer for the status csv file, so it will be handled the same as the scraper
            if self.verbose: print(f"Adding new restaurant ID {restaurant_id} to status CSV file.")
            new_row = pd.DataFrame({'id': [restaurant_id], 'has_website': [False],  'is_scraped': [True], 'is_filtered': [False]})
            self.status_df = pd.concat([self.status_df, new_row], ignore_index=True)
        else:
            # check if the column 'is_filtered' is already True
            if self.status_df.loc[self.status_df['id'] == restaurant_id, 'is_filtered'].values[0]:
                if self.verbose: print(f"Images for restaurant ID {restaurant_id} are already filtered.")
                return 0, 0

        # evaluate if the images are food or not food
        food_images = 0
        removed_images = 0 # count of images that were removed
        for image_file in os.listdir(image_dir):
            # Check if the file is an image with a valid extension
            if not image_file.endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
                continue

            image_path = os.path.join(image_dir, image_file)
            if not os.path.isfile(image_path):
                continue
            try:
                prediction = self.model.predict(image_path)
                if prediction == "food":
                    food_images += 1
                else:
                    # Remove the image if it is not food
                    os.remove(image_path)
                    removed_images += 1
            except Exception as e:
                print(f"Error processing image {image_file}: {e}")
                continue

        # if the food images list is empty, remove the directory
        if food_images == 0:
            if self.verbose: print(f"No food images found for restaurant ID {restaurant_id}. Removing directory: {image_dir}")
            os.rmdir(image_dir)

        # update the status 'is_filtered' for the row with the restaurant_id
        self.status_df.loc[self.status_df['id'] == restaurant_id, 'is_filtered'] = True

        if self.verbose: print(f"Filtered {food_images} food images and removed {removed_images} non-food images for restaurant ID {restaurant_id}.")

        # return the list of the food images and the count of removed images
        return food_images, removed_images

    def write_status(self):
        if self.verbose: print(f"Writing status CSV file: {self.status_csv_file}")
        self.status_df.to_csv(self.status_csv_file, index=False)


if __name__ == "__main__":
    # Example usage
    food_filter = FoodOrNotFoodFilter(os.path.join("..", "..", "modelling", "food_or_not_food", "food_or_not_food_model.pth"))

    total_food_images = 0
    total_removed_images = 0
    # number of restaurants without images after filtering
    number_of_res_without_images = 0

    # get the list of all the restaurants dir and iterate over them
    errors = 0
    for restaurant_dir in os.listdir("scraped-data"):
        image_directory = os.path.join("scraped-data", restaurant_dir, "images")

        # try to filter the images
        try:
            food, removed = food_filter.filter_images(image_directory)
            total_food_images += food
            total_removed_images += removed

            # if there are no food images left, increment the counter
            if food == 0 and removed != 0:
                number_of_res_without_images += 1
        except Exception as e:
            errors += 1
            print(f"Error filtering images for restaurant {restaurant_dir}: {e}")
            continue

    # write the status CSV file
    food_filter.write_status()

    print(f"Total number of errors encountered: {errors}")

    # if the statistics file already exists, get the old statistics
    stats_file = "food_filter_stats.json"
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            stats = json.load(f)

        # update the statistics with the new values
        stats["total_food_images"] += total_food_images
        stats["total_removed_images"] += total_removed_images
        stats["number_of_res_without_images"] += number_of_res_without_images
        stats["errors"] += errors
    else:
        stats = {
            "total_food_images": total_food_images,
            "total_removed_images": total_removed_images,
            "number_of_res_without_images": number_of_res_without_images,
            "errors": errors
        }

    # save the statistics to the file
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=4)




