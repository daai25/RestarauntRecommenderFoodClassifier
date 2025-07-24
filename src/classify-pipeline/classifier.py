import torch
from torchvision import models, transforms

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))


import src.resnet_loader.resnet50_loader as resnet_loader
import torch.nn as nn
from PIL import Image
import os
import json


def classify_images(image_directory: str, model_path: str, out_features: int = 78):
    """
    Main function to classify images in a directory using a pre-trained ResNet50 model.
    Args:
        image_directory (str): Path to the directory containing images to classify.
        model_path (str): Path to the pre-trained model file.
        out_features (int): Number of output features for the model (default is 78).
    Returns:
        tuple: Top 3 cuisine type guesses based on the model's predictions.
    """

    model, device, transform = load_classifier(model_path, out_features)
    print(
        f"Model loaded successfully from {model_path} with {out_features} output features."
    )
    print(f"Model is on device: {device}")

    # load JSON-mapping
    with open("food_cuisine_mapping.json", "r") as f:
        class_mapping = json.load(f)

    # Get the list of class names in the order your model uses
    class_names = list(
        class_mapping.keys()
    )  # Ensure this order matches your model's output order!

    cuisine_type_count = {}

    # Loop through images in the directory and apply the model
    for filename in os.listdir(image_directory):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(image_directory, filename)
            image = Image.open(image_path).convert("RGB")
            image_tensor = transform(image).unsqueeze(0).to(device)

            # run image through the model
            with torch.no_grad():
                # 1) Run the model and get logits
                logits = model(image_tensor)

                # 2) Compute probabilities
                probs = torch.nn.functional.softmax(
                    logits, dim=1
                )  # shape [1, out_features]

                # 3) Get your top-1 prediction and its probability
                top_prob, top_idx = probs.max(dim=1)  # tensors of shape [1]
                top_prob = top_prob.item()  # float
                top_idx = top_idx.item()  # int
                class_name = class_names[int(top_idx)]
                cuisine_types = class_mapping[class_name]

                print(f"✅  class {class_name}   {top_prob:.4f}  ({top_prob:.2%})")
                print(f"    Cuisine types: {cuisine_types}")

                # Count cuisine types
                for cuisine in cuisine_types:
                    cuisine_type_count[cuisine] = cuisine_type_count.get(cuisine, 0) + 1

    # get 3 most common cuisine types if there are enough
    sorted_cuisines = sorted(
        cuisine_type_count.items(), key=lambda x: x[1], reverse=True
    )
    top_cuisines = sorted_cuisines[:3] if len(sorted_cuisines) >= 3 else sorted_cuisines
    
    guess_1 = top_cuisines[0][0] if len(top_cuisines) > 0 else None
    guess_2 = top_cuisines[1][0] if len(top_cuisines) > 1 else None
    guess_3 = top_cuisines[2][0] if len(top_cuisines) > 2 else None
    
    print("\nTop cuisine type guesses:")
    print(f"1. {guess_1} ({cuisine_type_count.get(guess_1, 0)})")
    print(f"2. {guess_2} ({cuisine_type_count.get(guess_2, 0)})")
    print(f"3. {guess_3} ({cuisine_type_count.get(guess_3, 0))})")  
    
    return guess_1, guess_2, guess_3
    


def load_classifier(
    model_path: str, out_features: int = 2
) -> tuple[nn.Module, torch.device, transforms.Compose]:
    """
    Uses the resnet50_loader to load a pre-trained ResNet50 model.
    """

    return resnet_loader.load_resnet50_model(
        model_path=model_path, out_features=out_features
    )


if __name__ == "__main__":
    print("Test-RUN\n")

    MODEL_PATH = "./food_classifier_RESNET50.pth"
    OUT_FEATURES = 78
    IMAGE_DIRECTORY = "./test_images"
    classify_images(IMAGE_DIRECTORY, MODEL_PATH, OUT_FEATURES)
