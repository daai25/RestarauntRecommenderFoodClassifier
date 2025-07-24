# evaluation/food_or_not_food/model_evaluation.py
from typing import Any
import os
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import precision_recall_fscore_support
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from tqdm import tqdm

import src.resnet_loader as resnet_loader

# path to resnet 18 model, trained on the base dataset without augmentation
# (same as v1 in image_filter)
RESNET18_BASE_NO_AUG_PATH = "food_or_not_food_resnet18_base_no_aug.pth"

# path to resnet 18 model, trained on the base dataset with augmentation
RESNET18_BASE_AUG_PATH = "food_or_not_food_resnet18_base_aug.pth"

# path to resnet 18 model, trained on the improved dataset with augmentation run 1
# (same as v2 in image_filter)
RESNET18_IMPROVED_AUG_RUN1_PATH = "food_or_not_food_resnet18_improved_aug_run1.pth"

# path to resnet 18 model, trained on the improved dataset with augmentation run 2
RESNET18_IMPROVED_AUG_RUN2_PATH = "food_or_not_food_resnet18_improved_aug_run2.pth"

# path to resnet 50 model, trained on the improved dataset with augmentation
# (same as v3 in image_filter)
RESNET50_IMPROVED_AUG_PATH = "food_or_not_food_resnet50_improved_aug.pth"

def load_models() -> list[tuple[nn.Module, torch.device, transforms.Compose]]:
    resnet18_base_no_aug = resnet_loader.load_resnet18_model(
        RESNET18_BASE_NO_AUG_PATH,
        out_features=2
    )

    resnet18_base_aug = resnet_loader.load_resnet18_model(
        RESNET18_BASE_AUG_PATH,
        out_features=2
    )

    resnet18_improved_aug_run1 = resnet_loader.load_resnet18_model(
        RESNET18_IMPROVED_AUG_RUN1_PATH,
        out_features=2
    )

    # resnet18_improved_aug_run2 = resnet_loader.load_resnet18_model(
    #     RESNET18_IMPROVED_AUG_RUN2_PATH,
    #     out_features=2
    # )

    resnet50_improved_aug = resnet_loader.load_resnet50_model(
        RESNET50_IMPROVED_AUG_PATH,
        out_features=2
    )

    return [resnet18_base_no_aug, resnet18_base_aug,
            resnet18_improved_aug_run1, resnet50_improved_aug]

def load_data(transform: transforms.Compose, directory: str) -> DataLoader:
    dataset = ImageFolder(directory, transform=transform)
    return DataLoader(dataset, batch_size=64, num_workers=8, shuffle=False)


def evaluate_model(model: nn.Module, device: torch.device, dataloader: DataLoader) -> dict[str, float | Any]:
    all_predictions = []
    all_labels = []
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating model", unit="batch"):
            inputs, labels = batch
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # calculate the accuracy
    accuracy = sum([p == t for p, t in zip(all_predictions, all_labels)]) / len(all_labels)

    # calculate precision, recall, and F1-score
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_predictions, average="binary" if len(set(all_labels)) == 2 else "macro"
    )

    # calculate the confusion matrix
    cm = confusion_matrix(all_labels, all_predictions)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "confusion_matrix": cm,
    }

def plot_results(results: list[dict[str, float | Any]], model_names: list[str]):
    """
    Plot the evaluation results of multiple models.

    1. Bar chart for accuracy.
    2. Grouped bar chart for precision, recall, and F1-score.
    """
    assert len(results) == len(model_names), "Mismatch between number of results and model names"

    accuracies = [res["accuracy"] for res in results]
    precisions = [res["precision"] for res in results]
    recalls = [res["recall"] for res in results]
    f1_scores = [res["f1_score"] for res in results]

    x = np.arange(len(model_names))  # label locations

    # --- Accuracy bar chart ---
    plt.figure(figsize=(10, 6))
    plt.bar(x, accuracies, color='skyblue')
    plt.xticks(x, model_names, rotation=45, ha='right')
    plt.ylabel("Accuracy")
    plt.title("Model Accuracy Comparison")
    plt.ylim(0.8, 1)
    plt.tight_layout()
    plt.grid(axis='y')
    plt.show()

    # --- Grouped bar chart for precision, recall, and F1 ---
    width = 0.25  # width of each bar

    plt.figure(figsize=(12, 6))
    plt.bar(x - width, precisions, width, label='Precision', color='mediumseagreen')
    plt.bar(x, recalls, width, label='Recall', color='cornflowerblue')
    plt.bar(x + width, f1_scores, width, label='F1-Score', color='salmon')

    plt.xticks(x, model_names, rotation=45, ha='right')
    plt.ylabel("Score")
    plt.title("Model Evaluation: Precision, Recall, F1-Score")
    plt.ylim(0.8, 1)
    plt.legend(loc='lower left')
    plt.tight_layout()
    plt.grid(axis='y')
    plt.show()

def plot_confusion_matrix(eval_results: dict, title: str, labels=None):
    if labels is None:
        labels = ["Food", "Not Food"]

    cm = eval_results["confusion_matrix"]
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap=plt.cm.Blues)
    plt.xticks(ticks=np.arange(len(labels)), labels=labels, rotation=45)
    plt.yticks(ticks=np.arange(len(labels)), labels=labels)
    plt.title(f"Confusion Matrix: {title}")
    plt.show()

def main(evaluated_results: list[dict[str, float | Any]]=None):
    if evaluated_results is None:
        print("Loading models...")
        list_of_models = load_models()

        (resnet18_base_no_aug_model,
         resnet18_device,
         resnet18_transform) = list_of_models[0]

        resnet18_base_aug_model = list_of_models[1][0]
        resnet18_improved_aug_model = list_of_models[2][0]
        resnet50_improved_aug_model, resnet50_device, resnet50_transform = list_of_models[3]

        print("Loading data...")
        test_data = os.path.relpath("test_data")
        resnet18_loader = load_data(resnet18_transform, test_data)
        resnet50_loader = load_data(resnet50_transform, test_data)

        print("Evaluating models...")
        evaluated_results = [evaluate_model(resnet18_base_no_aug_model, resnet18_device, resnet18_loader),
                   evaluate_model(resnet18_base_aug_model, resnet18_device, resnet18_loader),
                   evaluate_model(resnet18_improved_aug_model, resnet18_device, resnet18_loader),
                   evaluate_model(resnet50_improved_aug_model, resnet50_device, resnet50_loader)]

        print(f"Results: {evaluated_results}")

    print("Plotting results...")
    plot_results(evaluated_results, [
        "Resnet18 on Base without Aug",
        "Resnet18 on Base with Aug",
        "Resnet18 on Improved with Aug",
        "Resnet50 on Improved with Aug"
    ])

    print("Plotting confusion matrices...")
    plot_confusion_matrix(evaluated_results[0], "Resnet18 on Base without Aug")
    plot_confusion_matrix(evaluated_results[1], "Resnet18 on Base with Aug")
    plot_confusion_matrix(evaluated_results[2], "Resnet18 on Improved with Aug")
    plot_confusion_matrix(evaluated_results[3], "Resnet50 on Improved with Aug")

if __name__ == "__main__":
    # these are the already calculated results from the evaluation
    last_results = [{
        'accuracy': 0.9502657555049354,
        'precision': 0.9749001711351968,
        'recall': 0.9515590200445434,
        'f1_score': 0.9630881938574246,
        'confusion_matrix': np.array(
            [[ 794,   44],
             [  87, 1709]])
    }, {
        'accuracy': 0.9582384206529992,
        'precision': 0.9647188533627343,
        'recall': 0.9743875278396437,
        'f1_score': 0.9695290858725761,
        'confusion_matrix': np.array(
            [[ 774,   64],
             [  46, 1750]])
    }, {
        'accuracy': 0.9688686408504176,
        'precision': 0.9766407119021134,
        'recall': 0.977728285077951,
        'f1_score': 0.9771841958820257,
        'confusion_matrix': np.array(
            [[ 796,   42],
             [  40, 1756]])
    }, {
        'accuracy': 0.9768413059984814,
        'precision': 0.9806094182825484,
        'recall': 0.9855233853006682,
        'f1_score': 0.9830602610386003,
        'confusion_matrix': np.array(
            [[ 803,   35],
             [  26, 1770]])
    }]

    main(evaluated_results=last_results)


