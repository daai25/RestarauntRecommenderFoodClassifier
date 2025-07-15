import os
from ImageFilterExtensionInterface import  ImageFilterExtensionInterface
import imagehash
from PIL import Image

def compute_file_hash_phash(path):
    with Image.open(path) as img:
        return imagehash.phash(img)

class SimilarHashImageFilter(ImageFilterExtensionInterface):
    """
    A filter that identifies and removes images that are similar based on perceptual hashing.
    This filter scans a directory for images, computes their hashes, and deletes those that are similar.
    """

    def __init__(self, verbose: bool=False, hamming_distance: int=5):
        """
        Initialize the SimilarHashImageFilter with a directory to scan for images.

        Args:
            verbose (bool): If True, print detailed information during processing.
            hamming_distance (int): Size of the hash to be computed for each image.
        """
        self.verbose = verbose
        self.hamming_distance = hamming_distance
        self.hash_map = {}  # to store hashes of processed images

    def filter_images(self, directory: str, statistics: dict, is_relative: bool, delete: bool) -> dict:
        """
        Scan the directory for images and apply filtering criteria based on perceptual hashing.

        Args:
            directory (str): Directory path to scan for images.
            statistics (dict): A dictionary to store statistics about the filtering process.
            is_relative (bool): If True, the directory path is relative; otherwise, it is absolute.
            delete (bool): If True, delete images that do not meet the criteria directly.
        Returns:
            dict: Updated statistics including counts of food and not food images, and any errors encountered.
        """
        self.hash_map = {} # reset the hash map for each filtering operation

        for root, _, files in os.walk(directory):
            for filename in files:
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    continue

                image_path = os.path.join(root, filename)

                # if the image is already in the filtered_image_paths set, skip it
                if image_path in statistics["filtered_image_paths"]:
                    continue

                # calculate the hashes of the images and store it in the hash_map with the respective image path
                try:
                    image_hash = compute_file_hash_phash(image_path)
                    similar_found = False
                    # if the hamming distance is less than or equal to the specified threshold, consider the images similar
                    for existing_hash, existing_path in self.hash_map.items():
                        if image_hash - existing_hash <= self.hamming_distance:
                            statistics["total_filtered"][self.__class__.__name__] += 1
                            similar_found = True
                            if delete:
                                os.remove(image_path)
                            else:
                                statistics["filtered_image_paths"].add(image_path)
                            break

                    if not similar_found:
                        # if no similar image found, add the hash to the map
                        self.hash_map[image_hash] = image_path
                except Exception as e:
                    if self.verbose:
                        print(f"Error processing {image_path}: {e}")
                    statistics["num_of_errors"] += 1
                    statistics["captured_errors"].append(str(e))

        return statistics