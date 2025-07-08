import os
import argparse

# command line example:
# python restaurant_image_exporter.py --data_dir scraped-data --output_dir C:\nfr\food_or_not_food_data\archive

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export restaurant images from a directory.")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to the data directory containing restaurant images.")
    parser.add_argument("--output_dir", type=str, required=True, help="Path to the output directory to save exported images.")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.abspath(__file__))
    # get the absolute paths to the directories
    data_dir = os.path.abspath(os.path.join(str(project_root), args.data_dir))
    output_dir = os.path.abspath(args.output_dir)

    # check if the data directory exists
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

    # check if the output directory exists
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    # create now the real used output directory
    output_dir = os.path.join(output_dir, "restaurant_images")
    if not os.path.exists(output_dir):
        print(f"Created output directory: {output_dir}")
        os.makedirs(output_dir)

    current_image_index = 0
    for restaurant_dir in os.listdir(data_dir):
        image_dir = os.path.join(data_dir, restaurant_dir, "images")

        # check if the image directory exists
        if not os.path.exists(image_dir):
            print(f"Image directory does not exist for restaurant {restaurant_dir}: {image_dir}")
            continue

        # iterate over all images in the image directory and copy them to the output directory
        for image_file in os.listdir(image_dir):
            image_path = os.path.join(image_dir, image_file)

            # check if the file is an image
            if not image_file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                print(f"Skipping non-image file: {image_path}")
                continue

            image_file_parts = image_file.split('.')
            if len(image_file_parts) != 2:
                print(f"Skipping file with invalid name format: {image_path}")
                continue

            image_ending = image_file_parts[1].lower()

            # construct the new image file name
            new_image_name = f"{current_image_index}.{image_ending}"
            new_image_path = os.path.join(output_dir, new_image_name)

            # copy the image to the output directory
            try:
                with open(image_path, 'rb') as src_file:
                    with open(new_image_path, 'wb') as dest_file:
                        dest_file.write(src_file.read())
                print(f"Copied {image_path} to {new_image_path}")
                current_image_index += 1
            except Exception as e:
                print(f"Error copying {image_path}: {e}")