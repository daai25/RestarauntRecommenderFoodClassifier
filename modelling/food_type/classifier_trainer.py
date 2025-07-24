import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torchvision.models import ResNet50_Weights
from pathlib import Path
from torch.optim.lr_scheduler import OneCycleLR
from sklearn.metrics import confusion_matrix


DATA_DIR = Path(__file__).parent.parent / "data" / "dataset"

def main():
    device = setup_device()
    train_loader, val_loader, test_loader = setup_datasets_loaders()

    use_resnet = True

    patience = 4  # Early stopping patience
    epochs_no_improve = 0
    num_epochs = 100

    if use_resnet:

        model_path = "food_101_classifier_filtered_classes_old.pth"

        model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)

        # replace final layer for food classification
        in_features = int(model.fc.in_features)

        model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, 78)  # 100 classes: all food categories
        )

        # freeze early layers
        for name, param in model.named_parameters():
            # unfreeze layer4, layer3, and fc layers
            if name.startswith("layer4") or name.startswith("layer3") or name.startswith("fc"):
                param.requires_grad = True
            else:
                param.requires_grad = False

        model = model.to(device, memory_format=torch.channels_last)

    else:

        print("setup Parameter 'use_resnet' wrongly to 'False'. ")

    print("Model finished setup.")

    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)

    # - Differential LRs -
    # backbone at 1e-5, classifier head at 1e-4
    backbone_params = [p for n, p in model.named_parameters() if "fc" not in n]
    head_param = [p for n, p in model.named_parameters() if "fc" in n]
    optimizer = optim.AdamW([
        {"params": backbone_params, "lr": 2e-4, "weight_decay": 1e-2},
        {"params": head_param, "lr": 2e-3, "weight_decay": 1e-2}
    ], lr=1e-3, weight_decay=1e-4)

    # - Scheduler -
    # Cosine Annealing over all epochs
    # scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    #     optimizer,
    #     T_max = num_epochs
    # )

    # OneCycleLR scheduler
    scheduler = OneCycleLR(
        optimizer,
        max_lr=[2e-4, 2e-3], # max LR for backbone and head
        total_steps=num_epochs * len(train_loader),
        pct_start=0.3, div_factor=25, final_div_factor=1e4
    )

    best_val_acc = 0.0

    print("Starting training...")

    for epoch in range(1, num_epochs + 1):

        if epoch == 10:
            for name, p in model.named_parameters():
                if name.startswith("layer2") or name.startswith("layer1"):
                    p.requires_grad = True

        # --- Training Phase ---
        model.train()
        running_loss = 0.0
        correct, total = 0, 0

        for images, labels in train_loader:
            images = images.to(device, memory_format=torch.channels_last, non_blocking=True)
            images = images.contiguous()
            labels = labels.to(device, non_blocking=True)

            optimizer.zero_grad() # zero the parameter gradients
            outputs = model(images)
            loss = criterion(outputs, labels) # criterion computes the loss
            loss.backward() # backpropagate the loss
            optimizer.step() # update the parameters
            scheduler.step() # Step the scheduler

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_loss = running_loss / len(train_loader.dataset)
        train_acc = correct / total

        # --- Validation Phase ---
        model.eval()

        val_correct, val_total = 0, 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)
        val_acc = val_correct / val_total

        print(f"Epoch {epoch:02d}: "
              f"Train Loss={train_loss:.4f}, Train Acc={train_acc:.3f} | "
              f"Val Acc={val_acc:.3f}")

        # save the model if validation accuracy improves
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            epochs_no_improve = 0 # reset counter
            torch.save(model.state_dict(), model_path)
            print(f"Model saved with validation accuracy: {best_val_acc:.3f}")
        else:
            epochs_no_improve += 1

        if epochs_no_improve >= patience:
            print(f"Early stopping at epoch {epoch}")
            break

    # Evaluate the model on the test set
    evaluate_model(model, test_loader, device, model_path)


def setup_device():
    """
    Sets up the device for training based on availability of hardware.
    Checks for MPS (Metal Performance Shaders) on macOS, CUDA for NVIDIA GPUs,
    and defaults to CPU if neither is available.

    Returns:
        torch.device: The device to be used for training (MPS, CUDA, or CPU).
    """

    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    print("Training on device:", device)

    return device

train_transform = transforms.Compose([
    transforms.RandomRotation(30), # rotate ±30°
    transforms.RandomHorizontalFlip(), # flip p=0.5
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.1), # varying brightness/contrast/sat/hue
    transforms.AutoAugment(transforms.AutoAugmentPolicy.IMAGENET),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def setup_datasets_loaders() -> tuple:
    """
    Sets up the datasets and data loaders for training, validation, and testing.
    Returns:
        Tuple: (train_loader, val_loader, test_loader)
    """
    train_ds = datasets.ImageFolder(f"{DATA_DIR}/train", transform=train_transform)
    val_ds = datasets.ImageFolder(f"{DATA_DIR}/validation", transform=val_transform)
    test_ds = datasets.ImageFolder(f"{DATA_DIR}/test", transform=val_transform)

    train_loader = DataLoader(train_ds, batch_size=256, shuffle=True, num_workers=10, persistent_workers=True, prefetch_factor=4)
    val_loader = DataLoader(val_ds, batch_size=256, shuffle=False, num_workers=10, persistent_workers=True, prefetch_factor=4)
    test_loader = DataLoader(test_ds, batch_size=256, shuffle=False, num_workers=10, persistent_workers=True, prefetch_factor=4)

    return train_loader, val_loader, test_loader

def evaluate_model(model, test_loader, device, model_path):
    """
    Evaluates the model on the test dataset and prints the accuracy.

    Args:
        model (torch.nn.Module): The trained model to evaluate.
        test_loader (torch.utils.data.DataLoader): DataLoader for the test dataset.
        device (torch.device): The device to run the evaluation on (CPU or GPU).
        model_path (str): Path to the saved model weights.
    """

    model.load_state_dict(torch.load(model_path))
    model.eval()
    test_correct, test_total = 0, 0
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            test_correct += (preds == labels).sum().item()
            test_total += labels.size(0)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    print("#" * 20, "\n\n")
    print("Final Test Accuracy:", test_correct / test_total)

    print("\n\n", "Confusion Matrix:")
    cm = confusion_matrix(all_labels, all_preds)
    print(cm)



if __name__ == "__main__":

    only_testing = False

    if only_testing:
        # --- Setup for evaluation only ---
        device = setup_device()
        _, _, test_loader = setup_datasets_loaders()

        # Recreate the exact model architecture you saved
        model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
        in_features = int(model.fc.in_features)
        model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, 78)
        )
        model = model.to(device, memory_format=torch.channels_last)

        # Path to your saved weights
        model_path = "food_101_classifier_filtered_classes_old.pth"

        # Run evaluation
        evaluate_model(model, test_loader, device, model_path)
    else:
        main()
        print("Training and evaluation completed successfully.")
