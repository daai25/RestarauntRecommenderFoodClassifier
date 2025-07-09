import os
from PIL import Image
import numpy as np

def is_placeholder_image(image_path, verbose=False):
    try:
        img = Image.open(image_path).convert('L')  # Convert to grayscale
        arr = np.array(img) / 255.0  # Normalize to 0–1
    except Exception as e:
        if verbose: print(f"Error opening {image_path}: {e}")
        return False

    black_ratio = np.mean(arr < 0.1)
    white_ratio = np.mean(arr > 0.9)
    std_dev = np.std(arr)

    if verbose:
        print(f"{image_path} | black: {black_ratio:.2f}, white: {white_ratio:.2f}, std: {std_dev:.4f}")

    return (
            0.599 < black_ratio < 0.66 and
            0.10 < white_ratio < 0.16 and
            0.3615 < std_dev < 0.381
    )


class PlaceholderImageFilter:
    def __init__(self, directory, directory_relative: bool=True, verbose: bool=False):
        """
        Initialize the PlaceholderImageFilter with a directory to scan for placeholder images.

        Raises:
            FileNotFoundError: If the specified directory does not exist.
        """
        # use either the relative or absolute path for the directory
        if directory_relative:
            self.directory = os.path.relpath(directory)
        else:
            self.directory = os.path.abspath(directory)

        self.verbose = verbose

        # check if the directory exists
        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"Directory does not exist: {self.directory}")

    def filter_images(self):
        """
        Scan the directory for images that are likely placeholders or text on a black background.
        Deletes these images if they match the criteria.

        Returns:
            int: The number of placeholder-like images deleted.
        """
        print(f"Scanning for placeholder images in: {self.directory}")
        deleted = 0

        for root, _, files in os.walk(self.directory):
            for filename in files:
                path = os.path.join(root, filename)
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                    continue

                if is_placeholder_image(path, verbose=self.verbose):
                    try:
                        os.remove(path)
                        if self.verbose: print(f"Deleted: {path}")
                        deleted += 1
                    except Exception as e:
                        if self.verbose: print(f"Error deleting {path}: {e}")

        print(f"\nDone. {deleted} placeholder-like image(s) deleted.")
        return deleted

if __name__ == "__main__":
    placeholder_filter = PlaceholderImageFilter("C:/nfr/food_or_not_food_data/archive/restaurant_images", directory_relative=False)
    placeholder_filter.filter_images()
