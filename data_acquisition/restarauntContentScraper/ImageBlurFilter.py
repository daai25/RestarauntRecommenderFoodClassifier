import os
import cv2

class ImageBlurFilter:
    def __init__(self, directory, blur_threshold=100.0, directory_relative=True, verbose=False):
        """
        Initialize the ImageBlurFilter.

        Args:
            directory (str): The path to the directory containing images.
            blur_threshold (float): Images with lower Laplacian variance will be considered blurred.
            directory_relative (bool): If True, uses a relative path; otherwise, uses an absolute path.
            verbose (bool): If True, prints detailed information.
        """
        if directory_relative:
            self.directory = os.path.relpath(directory)
        else:
            self.directory = os.path.abspath(directory)

        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"Directory does not exist: {self.directory}")

        self.blur_threshold = blur_threshold
        self.verbose = verbose

    def blur_score(self, image_path):
        """
        Compute the Laplacian variance of the image.

        Args:
            image_path (str): Full path to the image.

        Returns:
            float: Laplacian variance (higher = sharper).
        """
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise ValueError("Image could not be read or is not a valid image file.")
            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
            return laplacian_var
        except Exception as e:
            if self.verbose: print(f"Error processing {image_path}: {e}")
            return None

    def filter_images(self):
        """
        Scan the directory and delete blurred images.
        """
        if self.verbose: print(f"Scanning for blurred images in: {self.directory}")
        deleted_count = 0

        for root, _, files in os.walk(self.directory):
            for filename in files:
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')):
                    continue  # skip non-image files
                path = os.path.join(root, filename)
                score = self.blur_score(path)

                if score is None:
                    continue  # Skip unreadable images

                if score < self.blur_threshold:
                    try:
                        os.remove(path)
                        deleted_count += 1
                        if self.verbose:
                            print(f"Deleted blurred image: {path} (score: {score:.2f})")
                    except Exception as e:
                        if self.verbose:
                            print(f"Error deleting {path}: {e}")
                elif self.verbose:
                    print(f"Kept image: {path} (score: {score:.2f})")

        print(f"Finished deleting {deleted_count} blurred image(s).")



if __name__ == "__main__":
    blur_filter = ImageBlurFilter(
        directory="C:/nfr/food_or_not_food_data/archive/restaurant_images_labeled_similar",
        blur_threshold=100.0,
        directory_relative=False,
        verbose=False
    )
    blur_filter.filter_images()