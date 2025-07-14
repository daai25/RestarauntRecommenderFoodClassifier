import ImageFilterExtensionInterface
import cv2
import os
import hashlib
import numpy as np

def compute_file_hash(path, block_size=65536):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(block_size):
            hasher.update(chunk)
    return hasher.hexdigest()

class ImageFilter:
    """
    A class that applies various standard image filtering methods and also allows for custom extensions.

    All the filtered images will be deleted from the directory.
    """
    def __init__(self, filter_extensions: list, blur_threshold: float=100.0, uniform_tolerance: float=0.01):
        """
        Initialize the ImageFilter with a list of filter extensions.

        Args:
            filter_extensions (list): List of filter extension instances.
        Raises:
            TypeError: If any of the provided filter extensions do not implement the ImageFilterExtensionInterface.
        """
        for ext in filter_extensions:
            if not isinstance(ext, ImageFilterExtensionInterface.ImageFilterExtensionInterface):
                raise TypeError(f"Expected an instance of ImageFilterExtensionInterface, got {type(ext)}")

        self.filter_extensions = filter_extensions
        self.blur_threshold = blur_threshold
        self.uniform_tolerance = uniform_tolerance
        self.image_hash_map = {} # to store hashes of processed images

    def _is_blurry(self, image_path: str) -> bool:
        """
        Calculate the blur score of an image using Laplacian variance.

        Args:
            image_path (str): Full path to the image file.
        Returns:
            bool: True if the image is considered blurred (Laplacian variance below the threshold), False otherwise.
        Raises:
            FileNotFoundError: If the image file does not exist.
            ValueError: If the image cannot be read or is not a valid image file.
        """
        # check if the image file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("Image could not be read or is not a valid image file.")
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        return laplacian_var < self.blur_threshold

    def _is_uniform(self, image_path: str) -> bool:
        """
        Check if the image is uniform by calculating the standard deviation of pixel values.

        Args:
            image_path (str): Full path to the image file.
        Returns:
            bool: True if the image is considered uniform (standard deviation below the tolerance), False otherwise.
        Raises:
            FileNotFoundError: If the image file does not exist.
            ValueError: If the image cannot be read or is not a valid image file.
        """
        # check if the image file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Image could not be read or is not a valid image file.")

        # normalize to range [0.0, 1.0]
        img = img.astype(np.float32) / 255.0

        # calculate the standard deviation across all channels
        std_per_channel = img.std(axis=(0, 1))

        return bool(np.all(std_per_channel < self.uniform_tolerance))

    def _is_duplicate(self, image_path: str) -> bool:
        """
        Check if the image is a duplicate by comparing its hash with previously processed images.
        Args:
            image_path (str): Full path to the image file.
        Returns:
            bool: True if the image is a duplicate, False otherwise.
        Raises:
            FileNotFoundError: If the image file does not exist.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        file_hash = compute_file_hash(image_path)
        if file_hash in self.image_hash_map:
            return True
        else:
            self.image_hash_map[file_hash] = image_path
            return False

    def filter_images(self, directory: str, is_relative: bool=True) -> dict:
        """

        """
        self.image_hash_map = {}  # reset the hash map for each filtering operation

        if is_relative:
            directory = os.path.relpath(directory)
        else:
            directory = os.path.abspath(directory)

        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory does not exist: {directory}")

        return {}