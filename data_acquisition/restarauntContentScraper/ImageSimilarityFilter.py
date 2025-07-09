import os
import shutil
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import networkx as nx
from tqdm import tqdm

def _get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


class ImageSimilarityFilter:
    def __init__(self, directory, output_directory, threshold=0.95, directory_relative=True, verbose=False):
        """
        Initialize the ImageSimilarityFilter to find and group similar images.

        Args:
            directory (str): Path to the image folder.
            output_directory (str): Path to save grouped similar images.
            threshold (float): Cosine similarity threshold above which images are considered similar.
            directory_relative (bool): Whether paths are relative.
            verbose (bool): Print progress details.
        """
        self.directory = os.path.relpath(directory) if directory_relative else os.path.abspath(directory)
        self.output_directory = os.path.relpath(output_directory) if directory_relative else os.path.abspath(output_directory)
        self.threshold = threshold
        self.verbose = verbose

        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"Directory does not exist: {self.directory}")
        os.makedirs(self.output_directory, exist_ok=True)

        self.model = self._load_model()
        self.transform = _get_transform()

    def _load_model(self):
        """
        Load the pre-trained ResNet18 model and prepare it for feature extraction.
        """
        weights = ResNet18_Weights.DEFAULT
        model = resnet18(weights=weights)
        model = torch.nn.Sequential(*list(model.children())[:-1])  # remove classification head
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        self.device = device
        return model

    def _extract_feature(self, image_path):
        """
        Extract features from an image using the pre-trained model.
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

    def _create_embeddings(self) -> tuple[list[str], np.ndarray]:
        """
        Create embeddings for all images in the directory.
        """
        images = []
        embeddings = []
        for root, _, files in os.walk(self.directory):
            for file in tqdm(files, desc="Extracting features", unit=" images"):
                if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
                    full_path = os.path.join(root, file)
                    feat = self._extract_feature(full_path)
                    if feat is not None:
                        embeddings.append(feat)
                        images.append(full_path)

        embeddings = np.array(embeddings)
        return images, embeddings

    def _create_groups(self) -> tuple[list[set[int]], list[str]]:
        """
        Create groups of similar images based on cosine similarity.
        """
        if self.verbose:
            print(f"Process Image(s) in: {self.directory}")

        images, embeddings = self._create_embeddings()

        similarity_matrix = cosine_similarity(embeddings)

        if self.verbose:
            print("Generate graph of similar images...")

        G = nx.Graph()
        for i in tqdm(range(len(images)), desc="Create nodes", unit=" images"):
            G.add_node(i)
            for j in range(i + 1, len(images)):
                if similarity_matrix[i, j] >= self.threshold:
                    G.add_edge(i, j)

        return list(nx.connected_components(G)), images

    def filter_and_group_images(self):
        """
        Find similar images and group them into folders by similarity.
        """
        groups, images = self._create_groups()

        # Create output directories and copy similar images
        group_id = 0
        for group in groups:
            if len(group) <= 1:
                continue  # Einzelbilder überspringen

            group_folder = os.path.join(self.output_directory, f"group_{group_id:03d}")
            os.makedirs(group_folder, exist_ok=True)

            for idx in group:
                img_path = images[idx]
                dest_path = os.path.join(group_folder, os.path.basename(img_path))
                shutil.copy2(img_path, dest_path)
                if self.verbose:
                    print(f"Kopiert {img_path} -> {dest_path}")

            group_id += 1

        print(f"{group_id} similar group(s) created in {self.output_directory}.")

    def filter_and_delete_images(self):
        """
        Filter all images that are similar to each other based on cosine similarity.

        Keeps only one image from each group of similar images.
        """
        groups, images = self._create_groups()

        deleted_count = 0
        for group in groups:
            if len(group) <= 1:
                continue  # Skip single images

            group = list(group)
            # Keep the first image in the group and delete the rest
            to_delete = group[1:]

            for idx in to_delete:
                img_path = images[idx]
                try:
                    os.remove(img_path)
                    deleted_count += 1
                    if self.verbose:
                        print(f"Deleted: {img_path}")
                except Exception as e:
                    if self.verbose:
                        print(f"Error deleting {img_path}: {e}")

        print(f"{deleted_count} similar Image(s) deleted.")


if __name__ == "__main__":
    image_similarity_filter = ImageSimilarityFilter(
        directory="C:/nfr/food_or_not_food_data/archive/restaurant_images_labeled_similar/food",
        output_directory="C:/nfr/food_or_not_food_data/similar_groups_food_test",
        threshold=0.97,
        directory_relative=False,
        verbose=True
    )
    image_similarity_filter.filter_and_delete_images()