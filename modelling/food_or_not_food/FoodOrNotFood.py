import torch
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
import os

class FoodOrNotFood:
    """
    A model for classifying images as "food" or "not food" using a pre-trained ResNet18 architecture.
    """

    def __init__(self, model_path="food_or_not_food_model.pth", device=None):
        """
        Initializes the FoodOrNotFood model for classifying images as "food" or "not food".

        Args:
            model_path (str): Path to the file with the trained model weights (.pth).
            device (str, optional): Device to use ('cuda', 'cpu'). If not specified, selected automatically.

        Raises:
            FileNotFoundError: If the specified model file does not exist.
        """
        # Set device to GPU if available, else CPU
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # Load pre-trained ResNet18 weights and transform
        self.weights = ResNet18_Weights.DEFAULT
        self.transform = self.weights.transforms()

        # Initialize the model
        self.model = resnet18(weights=self.weights)
        self.model.fc = nn.Linear(self.model.fc.in_features, 2)  # food / not food = 2 classes

        # Load trained weights
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        # Class labels
        self.class_names = ["food", "not food"]

    def predict(self, image_path):
        """
        Predicts whether the image at the given path is food or not food.

        Args:
            image_path (str): Path to the image file to classify.

        Returns:
            str: Predicted class label, either "food" or "not food".

        Raises:
            FileNotFoundError: If the specified image file does not exist.
        """
        # Check if image file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Load and transform the image
        image = Image.open(image_path).convert("RGB")
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)  # Add batch dimension

        # Perform inference
        with torch.no_grad():
            outputs = self.model(input_tensor)
            _, predicted = torch.max(outputs, 1)

        # Return the predicted class label
        return self.class_names[predicted.item()]