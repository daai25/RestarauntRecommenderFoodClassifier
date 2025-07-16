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

def is_monochrome_image(image_path, verbose=False):
    try:
        img = Image.open(image_path).convert('RGB')  # Convert to RGB
        arr = np.array(img) / 255.0  # Normalize to 0–1
    except Exception as e:
        if verbose: print(f"Error opening {image_path}: {e}")
        return False

    # Calculate the standard deviation of pixel values
    std_dev = np.std(arr)

    if verbose:
        print(f"{image_path} | std_dev: {std_dev:.6f}")

    # If the standard deviation of pixel values is very low, it's likely monochrome
    return std_dev < 0.01


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

    def filter_placeholder_images(self) -> tuple[list[str], int]:
        """
        Scan the directory for images that are likely placeholders or text on a black background.
        Deletes these images if they match the criteria.

        Returns:
            int: The number of placeholder-like images deleted.
        """
        print(f"Scanning for placeholder images in: {self.directory}")
        deleted = 0
        deleted_file_names = []

        for root, _, files in os.walk(self.directory):
            for filename in files:
                path = os.path.join(root, filename)
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                    continue

                if is_placeholder_image(path, verbose=self.verbose):
                    try:
                        os.remove(path)
                        if self.verbose: print(f"Deleted: {path}")
                        deleted_file_names.append(filename)
                        deleted += 1
                    except Exception as e:
                        if self.verbose: print(f"Error deleting {path}: {e}")

        print(f"\nDone. {deleted} placeholder-like image(s) deleted.")
        return deleted_file_names, deleted

    def filter_monochrome_images(self) -> tuple[list[str], int]:
        """
        Scan the directory for monochrome images and delete them.
        Monochrome images are those with very low standard deviation in pixel values.

        Returns:
            int: The number of monochrome images deleted.
        """
        print(f"Scanning for monochrome images in: {self.directory}")
        deleted = 0
        deleted_file_names = []

        for root, _, files in os.walk(self.directory):
            for filename in files:
                path = os.path.join(root, filename)
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                    continue

                if is_monochrome_image(path, verbose=self.verbose):
                    try:
                        os.remove(path)
                        if self.verbose: print(f"Deleted: {path}")
                        deleted_file_names.append(filename)
                        deleted += 1
                    except Exception as e:
                        if self.verbose: print(f"Error deleting {path}: {e}")

        print(f"\nDone. {deleted} monochrome image(s) deleted.")
        return deleted_file_names, deleted

if __name__ == "__main__":
    placeholder_filter = PlaceholderImageFilter(
        directory="C:/nfr/food_or_not_food_data/archive/restaurant_images_labeled_similar/non_food",
        directory_relative=False,
        verbose=False
    )
    file_names, num_del = placeholder_filter.filter_monochrome_images()
