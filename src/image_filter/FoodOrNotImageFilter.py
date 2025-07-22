# src/image_filter/FoodOrNotImageFilter.py
import os
import torch
from PIL import Image
import src.resnet_loader as resnet_loader

from .ImageFilterExtension import ImageFilterExtension
from .FilterStatistics import FilterStatistics

class FoodOrNotImageFilter(ImageFilterExtension):
    """
    A filter that classifies images as "food" or "not food" using a pre-trained ResNet18 model.
    This filter scans a directory for images, classifies them, and deletes those that are not food.
    """

    # valid model versions
    _valid_model_versions = ["v1", "v2", "v3"]

    def __init__(self, verbose: bool=False, version: str= "v3"):
        """
        Initialize the FoodOrNotImageFilter with a directory to scan for images.

        Args:
            verbose (bool): If True, print detailed information during processing.
            version (str): Version of the model to use for classification. Default is "v3".
        """
        super().__init__(verbose=verbose)

        current_dir = os.path.dirname(os.path.abspath(__file__))

        # validate the model version
        if version not in self._valid_model_versions:
            raise ValueError(f"Invalid model version: {version}. Valid versions are: {self._valid_model_versions}")
        model_name = "food_or_not_model_" + version + ".pth"

        model_path = os.path.join(current_dir, model_name)

        # load the classifier model
        if version == "v3":
            # load the pre-trained ResNet50 model
            self.model, self.device, self.transform =(
                resnet_loader.load_resnet50_model(
                    model_path=model_path,
                    out_features=2
                )
            )
        else:
            # load the pre-trained ResNet18 model
            self.model, self.device, self.transform = (
                resnet_loader.load_resnet18_model(
                    model_path=model_path,
                    out_features=2
                )
            )

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

    def _do_filtering(self, directory: str, statistics: FilterStatistics, delete: bool=True) -> FilterStatistics:
        """
        Scan the directory for images and classify them as food or not food.

        Args:
            directory (str): Path to the directory containing images.
            statistics (FilterStatistics): A data class to store statistics about the filtering process.
            delete (bool): If True, non-food images will be deleted. Defaults to True.
        Returns:
            FilterStatistics: Updated statistics including counts of food and not food images, and any errors encountered.
        """
        # walk through the directory and process each image
        for root, _, files in os.walk(directory):
            # go through each file in the directory
            for filename in files:
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    continue

                image_path = os.path.join(root, filename)

                # check if the image is already in the filtered_image_paths set
                if image_path in statistics.filtered_image_paths:
                    continue

                try:
                    # classify the image
                    result = self._classify_image(image_path)
                    if result != "food":
                        statistics.total_filtered[self.__class__.__name__] += 1
                        # remove non-food images if the delete flag is set
                        if delete:
                            os.remove(image_path)
                        else:
                            # only stores the path of non-food images, when the delete flag is False
                            statistics.filtered_image_paths.add(image_path)
                except Exception as e:
                    if self.verbose:
                        print(f"Error processing {image_path}: {e}")
                    statistics.num_of_errors += 1
                    statistics.captured_errors.append(str(e))

        return statistics