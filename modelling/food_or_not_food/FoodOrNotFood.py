import torch
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
import os

class FoodOrNotFood:
    def __init__(self, model_path="food_or_not_food_model.pth", device=None):
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
        self.class_names = ["not food", "food"]

    def predict(self, image_path):
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

        # Return the class label
        return self.class_names[predicted.item()]