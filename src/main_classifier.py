import sys
import os
from PIL import Image
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import src.classify_pipeline.classifier as classifier
import src.image_filter as image_filter
import src.classify_pipeline as classify_pipeline


def classify_restaurant(image_path):

    print(f"Classifying images in directory: {image_path}")

    # ----------------------------------
    # Clean up the images
    # ----------------------------------

    # create an instance of the FoodOrNotFoodImageFilter
    food_filter = image_filter.FoodOrNotImageFilter(version="v3")

    similarity_filter = image_filter.SimilarHashImageFilter(
        hamming_distance=5,
    )

    # create an instance of the ImageFilter
    img_filter = image_filter.ImageFilter(
        filter_extensions=[food_filter, similarity_filter], blur_threshold=80
    )

    filter_image_path = image_path

    # filter the images in the test images directory
    stats = img_filter.filter_images(filter_image_path, is_relative=False, delete=True)

    print(f"Filtered images: {stats.filtered_image_paths}")

    # ----------------------------------
    # Classify the images that are left
    # ----------------------------------

    # classify the images in the directory
    # Use absolute path for the model file
    project_root = Path(__file__).resolve().parents[1]
    model_path = str(
        project_root / "src" / "classify_pipeline" / "food_classifier_RESNET50.pth"
    )

    # Verify the model file exists
    if not os.path.exists(model_path):
        print(f"Model file not found at: {model_path}")
        return ["Model file not found"]

    out_features = 78  # Number of output features for the model
    cuisine_guesses = classifier.classify_images(
        image_directory=filter_image_path,
        model_path=model_path,
        out_features=out_features,
    )

    return list(cuisine_guesses)


if __name__ == "__main__":

    classify_restarant("./test_images/")
