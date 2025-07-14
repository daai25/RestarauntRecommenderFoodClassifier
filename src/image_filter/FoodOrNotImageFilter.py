import os
import torch
from torchvision import transforms
from PIL import Image
from torchvision.models import ResNet18_Weights

import ImageFilterExtensionInterface


class FoodOrNotImageFilter(ImageFilterExtensionInterface.ImageFilterExtensionInterface):
    """
    A filter that classifies images as "food" or "not food" using a pre-trained ResNet18 model.
    This filter scans a directory for images, classifies them, and deletes those that are not food.
    """

    def __init__(self, verbose: bool=False, use_new_model: bool=True):
        """
        Initialize the FoodOrNotImageFilter with a directory to scan for images.
        """
        self.verbose = verbose

        current_dir = os.path.dirname(os.path.abspath(__file__))
        if use_new_model:
            model_path = os.path.join(current_dir, 'food_or_not_model.pth')
        else:
            model_path = os.path.join(current_dir, 'food_or_not_model_old.pth')

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # load the classifier model
        self.model = torch.load(model_path, map_location=self.device)
        self.model.to(self.device)
        self.model.eval()

        weights = ResNet18_Weights.DEFAULT
        default_mean = weights.transforms().mean
        default_std = weights.transforms().std

        # define the transformation pipeline
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=default_mean, std=default_std),
        ])

        self.class_names = ["food", "not food"]

    def _classify_image(self, image_path: str) -> str:
        """
        Predict whether the image at the given path is food or not food.
        """
        # check if the image file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # load and transform the image
        image = Image.open(image_path).convert("RGB")
        image = self.transform(image).unsqueeze(0).to(self.device)

        # make prediction
        with torch.no_grad():
            output = self.model(image)
            _, predicted = torch.max(output, 1)

        return self.class_names[predicted.item()]

    def filter_images(self, directory: str, is_relative: bool=True, delete: bool=True) -> dict:
        """
        Scan the directory for images and classify them as food or not food.
        If they are not food, they will be deleted.

        Args:
            directory (str): Path to the directory containing images.
            is_relative (bool): Whether the path is relative or absolute. Defaults to True.
            delete (bool): If True, non-food images will be deleted. Defaults to True.
        Returns:
            dict: A dictionary containing statistics about the processed images.
                - total_files: Total number of files processed.
                - total_images: Total number of images processed.
                - food_images: Number of images classified as food.
                - not_food_images: Number of images classified as not food (and deleted).
                - not_food_images_path: List of paths of non-food images if delete is False.
                - total_errors: Total number of errors encountered during processing.
                - captured_errors: List of error messages encountered during processing.
        Raises:
            FileNotFoundError: If the specified directory does not exist.
        """
        # build the relative or absolute path for the directory
        if is_relative:
            directory = os.path.relpath(directory)
        else:
            directory = os.path.abspath(directory)

        # check if the directory exists
        if os.path.exists(directory):
            raise FileNotFoundError(f"Directory does not exist: {directory}")

        # prepare statistics structure
        statistics = {
            "total_files": 0,
            "total_images": 0,
            "food_images": 0,
            "not_food_images": 0,
            "not_food_images_path": [], # store paths of non-food images if delete is False
            "total_errors": 0,
            "captured_errors": [] # store any errors encountered during processing
        }

        # walk through the directory and process each image
        for root, _, files in os.walk(directory):
            # go through each file in the directory
            for filename in files:
                statistics["total_files"] += 1
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    continue

                image_path = os.path.join(root, filename)
                statistics["total_images"] += 1
                try:
                    # classify the image
                    result = self._classify_image(image_path)
                    if result == "food":
                        statistics["food_images"] += 1
                    else:
                        # remove non-food images if the delete flag is set
                        if delete:
                            os.remove(image_path)
                        else:
                            # only stores the path of non-food images, when the delete flag is False
                            statistics["not_food_images_path"].append(image_path)
                        statistics["not_food_images"] += 1
                except Exception as e:
                    if self.verbose:
                        print(f"Error processing {image_path}: {e}")
                    statistics["total_errors"] += 1
                    statistics["captured_errors"].append(str(e))

        return statistics