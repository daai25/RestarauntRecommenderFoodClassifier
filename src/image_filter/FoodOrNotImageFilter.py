import os
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
from torchvision.models import resnet18, ResNet18_Weights

from .ImageFilterExtension import ImageFilterExtension

class FoodOrNotImageFilter(ImageFilterExtension):
    """
    A filter that classifies images as "food" or "not food" using a pre-trained ResNet18 model.
    This filter scans a directory for images, classifies them, and deletes those that are not food.
    """
    def __init__(self, verbose: bool=False, use_new_model: bool=True):
        """
        Initialize the FoodOrNotImageFilter with a directory to scan for images.

        Args:
            verbose (bool): If True, print detailed information during processing.
            use_new_model (bool): If True, use the new model; otherwise, use the old model.
        """
        super().__init__(verbose=verbose)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        if use_new_model:
            model_path = os.path.join(current_dir, 'food_or_not_model.pth')
        else:
            model_path = os.path.join(current_dir, 'food_or_not_model_old.pth')

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # load the classifier model
        # load the pre-trained ResNet18 model
        weights = ResNet18_Weights.DEFAULT
        model = resnet18(weights=None)  # kein vortrainiertes Weight-Loading hier!

        # replace the final fully connected layer to match the number of classes (2: food, not food)
        model.fc = nn.Linear(model.fc.in_features, 2)

        # load the model state dictionary from the specified path
        model.load_state_dict(torch.load(model_path, map_location=self.device))

        # move the model to the appropriate device (GPU or CPU)
        model.to(self.device)
        model.eval()
        self.model = model

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

    def _do_filtering(self, directory: str, statistics: dict, delete: bool=True) -> dict:
        """
        Scan the directory for images and classify them as food or not food.

        Args:
            directory (str): Path to the directory containing images.
            statistics (dict): A dictionary to store statistics about the filtering process.
            delete (bool): If True, non-food images will be deleted. Defaults to True.
        Returns:
            dict: Updated statistics including counts of food and not food images, and any errors encountered.
        """
        # walk through the directory and process each image
        for root, _, files in os.walk(directory):
            # go through each file in the directory
            for filename in files:
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    continue

                image_path = os.path.join(root, filename)

                # check if the image is already in the filtered_image_paths set
                if image_path in statistics["filtered_image_paths"]:
                    continue

                try:
                    # classify the image
                    result = self._classify_image(image_path)
                    if result != "food":
                        statistics["total_filtered"][self.__class__.__name__] += 1
                        # remove non-food images if the delete flag is set
                        if delete:
                            os.remove(image_path)
                        else:
                            # only stores the path of non-food images, when the delete flag is False
                            statistics["filtered_image_paths"].add(image_path)
                except Exception as e:
                    if self.verbose:
                        print(f"Error processing {image_path}: {e}")
                    statistics["num_of_errors"] += 1
                    statistics["captured_errors"].append(str(e))

        return statistics