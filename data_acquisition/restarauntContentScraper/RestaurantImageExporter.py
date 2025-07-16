import os

class RestaurantImageExporter:

    def __init__(self, input_dir, output_dir, input_relative: bool=True, output_relative: bool=False, verbose: bool=False):
        """
        Initialize the RestaurantImageExporter with input and output directories.
        """
        # use either the relative or absolute path for the input and output directories
        if input_relative:
            self.input_dir = os.path.relpath(input_dir)
        else:
            self.input_dir = os.path.abspath(input_dir)

        if output_relative:
            self.output_dir = os.path.relpath(output_dir)
        else:
            self.output_dir = os.path.abspath(output_dir)

        self.verbose = verbose

        # prepare the directories
        self.prepare_directories()



    def prepare_directories(self):
        """
        Check if the input and output directories exist.

        If the output directory does not exist, it will be created.

        Also creates a subdirectory "restaurant_images" in the output directory.
        And assigns it to self.output_dir.

        Raises:
            FileNotFoundError: If the input directory does not exist.
        """
        if not os.path.exists(self.input_dir):
            raise FileNotFoundError(f"Input directory does not exist: {self.input_dir}")
        if not os.path.exists(self.output_dir):
            if self.verbose: print(f"Output directory does not exist: {self.output_dir}, creating it now.")
            os.makedirs(self.output_dir)

        self.output_dir = os.path.join(self.output_dir, "restaurant_images")
        os.makedirs(self.output_dir, exist_ok=True)

    def export_images(self):
        """
        Export images from the input directory to the output directory.
        """
        current_image_index = 0
        for restaurant_dir in os.listdir(self.input_dir):
            image_dir = os.path.join(self.input_dir, restaurant_dir, "images")

            # check if the image directory exists
            if not os.path.exists(image_dir):
                if self.verbose: print(f"Image directory does not exist for restaurant {restaurant_dir}: {image_dir}")
                continue

            # iterate over all images in the image directory and copy them to the output directory
            for image_file in os.listdir(image_dir):
                image_path = os.path.join(image_dir, image_file)

                # check if the file is an image
                if not image_file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    if self.verbose: print(f"Skipping non-image file: {image_path}")
                    continue

                image_file_parts = image_file.split('.')
                if len(image_file_parts) != 2:
                    if self.verbose: print(f"Skipping file with invalid name format: {image_path}")
                    continue

                image_ending = image_file_parts[1].lower()

                # construct the new image file name
                new_image_name = f"{current_image_index}.{image_ending}"
                new_image_path = os.path.join(self.output_dir, new_image_name)

                # copy the image to the output directory
                try:
                    with open(image_path, 'rb') as src_file:
                        with open(new_image_path, 'wb') as dest_file:
                            dest_file.write(src_file.read())
                    if self.verbose: print(f"Copied {image_path} to {new_image_path}")
                    current_image_index += 1
                except Exception as e:
                    print(f"Error copying {image_path}: {e}")

        print(f"Finished exporting images from {self.input_dir} to {self.output_dir}")


if __name__ == "__main__":
    exporter = RestaurantImageExporter("scraped-data", "C:/nfr/food_or_not_food_data/archive")
    exporter.export_images()