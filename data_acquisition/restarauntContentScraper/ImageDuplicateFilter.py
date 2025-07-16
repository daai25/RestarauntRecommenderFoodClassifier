import os
import hashlib

def compute_file_hash(path, block_size=65536):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(block_size):
            hasher.update(chunk)
    return hasher.hexdigest()

class ImageDuplicateFilter:
    def __init__(self, directory, directory_relative: bool=True, verbose: bool=False):
        """
        Initialize the ImageDuplicateFilter with a directory to scan for duplicate images.

        Args:
            directory (str): The path to the directory containing images.
            directory_relative (bool): If True, uses a relative path; otherwise, uses an absolute path.
            verbose (bool): If True, prints detailed information about the process.

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
        Scan the directory for duplicate images and delete them.
        """
        if self.verbose: print(f"Scanning for duplicate images in: {self.directory}")
        duplicates = []
        hash_map = {}

        for root, _, files in os.walk(self.directory):
            for filename in files:
                path = os.path.join(root, filename)
                try:
                    file_hash = compute_file_hash(path)
                except Exception as e:
                    if self.verbose: print(f"Error reading {path}: {e}")
                    continue

                if file_hash in hash_map:
                    if self.verbose: print(f"Duplicate found: {path} (identical to {hash_map[file_hash]})")
                    duplicates.append(path)
                else:
                    hash_map[file_hash] = path

        if self.verbose: print(f"Found {len(duplicates)} duplicate images")
        if self.verbose: print(f"Starting deletion...")
        # Delete duplicates
        for dup in duplicates:
            try:
                os.remove(dup)
                if self.verbose: print(f"Deleted: {dup}")
            except Exception as e:
                if self.verbose: print(f"Error deleting {dup}: {e}")

        print(f"Finished deleting {len(duplicates)} duplicate image(s).")



if __name__ == "__main__":
    duplicate_filter = ImageDuplicateFilter("C:/nfr/food_or_not_food_data/archive/restaurant_images", directory_relative=False)
    duplicate_filter.filter_images()
