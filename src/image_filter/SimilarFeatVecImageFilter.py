import os
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

from ImageFilterExtensionInterface import ImageFilterExtensionInterface

_weights = ResNet18_Weights.DEFAULT

def _get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=_weights.transforms().mean,
            std=_weights.transforms().std
        )
    ])

class SimilarFeatVecImageFilter(ImageFilterExtensionInterface):
    """
    A image filter extension that identifies and removes images that are similar based on feature vectors.
    """

    def __init__(self, verbose: bool=False, threshold: float=0.97):
        """
        Initialize the SimilarFeatVecImageFilter with a threshold for cosine similarity.

        Args:
            verbose (bool): If True, print detailed information during processing.
            threshold (float): Cosine similarity threshold for grouping similar images.
        """
        self.verbose = verbose
        self.threshold = threshold

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # init the used model
        self.model = resnet18(weights=_weights)
        self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
        self.model.to(self.device)
        self.model.eval()

        self.transform = _get_transform()

    def _extract_feature(self, image_path: str) -> torch.Tensor | None:
        """
        Extract features from an image using the pre-trained model.

        Args:
            image_path (str): Full path to the image file.
        Returns:
            torch.Tensor | None: Feature vector of the image, or None if an error occurs.
        """
        try:
            image = Image.open(image_path).convert('RGB')
            tensor = self.transform(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                features = self.model(tensor)
            return features.squeeze().cpu().numpy()
        except Exception as e:
            if self.verbose:
                print(f"Error processing {image_path}: {e}")
            return None

    def _create_embeddings(self, directory: str) -> tuple[list[str], np.ndarray]:
        """
        Create embeddings for all images in the directory.

        Args:
            directory (str): Path to the directory containing images.
        Returns:
            tuple: A tuple containing a list of image paths and a numpy array of embeddings.
        """
        images = []
        embeddings = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
                    full_path = os.path.join(root, file)
                    feat = self._extract_feature(full_path)
                    if feat is not None:
                        embeddings.append(feat)
                        images.append(full_path)

        embeddings = np.array(embeddings)
        return images, embeddings

    def _create_groups(self, directory: str) -> tuple[list[str], list[set[int]]]:
        """
        Create groups of similar images based on cosine similarity.

        Args:
            directory (str): Path to the directory containing images.
        Returns:
            tuple: A tuple containing a list of image paths and a list of sets of indices,
            representing groups of similar images.
        """
        if self.verbose:
            print(f"Process Image(s) in: {directory}")

        images, embeddings = self._create_embeddings(directory)

        similarity_matrix = cosine_similarity(embeddings)

        if self.verbose:
            print("Generate graph of similar images...")

        G = nx.Graph()
        for i in range(len(images)):
            G.add_node(i)
            for j in range(i + 1, len(images)):
                if similarity_matrix[i, j] >= self.threshold:
                    G.add_edge(i, j)

        return images, list(nx.connected_components(G))

    def filter_images(self, directory: str, statistics: dict, is_relative: bool, delete: bool) -> dict:
        """
        Scan the directory for images and group similar images based on feature vectors.

        Args:
            directory (str): Path to the directory containing images.
            statistics (dict): A dictionary to store statistics about the filtering process.
            is_relative (bool): If True, the directory path is relative; otherwise, it is absolute.
            delete (bool): If True, delete images that do not meet the criteria directly.
        Returns:
            dict: Updated statistics including counts of filtered images, and any errors encountered.
        Raises:
            FileNotFoundError: If the specified directory does not exist.
        """
        if is_relative:
            directory = os.path.relpath(directory)
        else:
            directory = os.path.abspath(directory)

        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory does not exist: {directory}")

        images, groups = self._create_groups(directory)

        for group in groups:
            # Skip groups with only one image
            if len(group) <= 1:
                continue

            group = list(group)
            # Keep the first image in the group and delete the rest
            selected = group[1:]

            for i in selected:
                image_path = images[i]

                if image_path in statistics["filtered_image_paths"]:
                    # Skip if the image is already in the filtered paths
                    continue

                statistics["total_filtered"][self.__class__.__name__] += 1
                if delete:
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        if self.verbose:
                            print(f"Error processing {image_path}: {e}")
                        statistics["num_of_errors"] += 1
                        statistics["captured_errors"].append(str(e))
                else:
                    # Add to filtered paths if not deleting
                    statistics["filtered_image_paths"].add(image_path)

        return statistics