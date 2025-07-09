import os
import argparse
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torchvision.models import resnet18, ResNet18_Weights
from torch.utils.data import DataLoader
from sklearn.metrics import precision_recall_fscore_support, classification_report

# command line example:
# python food_or_not_food_trainer.py --train_dir C:/nfr/food_or_not_food_data/archive/food_data/train --test_dir C:/nfr/food_or_not_food_data/archive/food_data/test --validation_dir C:/nfr/food_or_not_food_data/archive/food_data/validation

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a model to classify food or not food images.")
    parser.add_argument("--train_dir", type=str, required=True, help="Path to the training data directory")
    parser.add_argument("--test_dir", type=str, required=True, help="Path to the testing data directory")
    parser.add_argument("--validation_dir", type=str, required=False, help="Path to the validation data directory (optional)")
    parser.add_argument("--max_epochs", type=int, default=30, required=False, help="Number of epochs to train (default: 30) (optional)")
    args = parser.parse_args()

    # food or not food dataset archive with training and testing data
    train_dir = os.path.abspath(args.train_dir)
    test_dir = os.path.abspath(args.test_dir)

    # check if validation_dir is provided, if not, set it to the test_dir
    if args.validation_dir:
        validation_dir = os.path.abspath(args.validation_dir)
    else:
        print("No validation directory provided, using test directory for validation.")
        validation_dir = test_dir

    # get max_epochs from command line argument
    max_epochs = args.max_epochs

    # check if the directories exist and exit the program
    if not os.path.exists(train_dir):
        print(f"Training directory {train_dir} does not exist.")
        exit(1)
    if not os.path.exists(test_dir):
        print(f"Testing directory {test_dir} does not exist.")
        exit(1)

    # load the pre-trained ResNet18 model
    weights = ResNet18_Weights.DEFAULT
    model = resnet18(weights=weights)

    # define the transformations for the training data
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224), # random resized and crop to 224x224
        transforms.RandomHorizontalFlip(), # random horizontal flip
        transforms.RandomRotation(15), # random rotation
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1), # random color jitter
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),  # random translation
        transforms.RandomVerticalFlip(p=0.1), # random vertical flip
        transforms.RandomGrayscale(p=0.1), # random grayscale conversion
        transforms.ToTensor(),
        transforms.Normalize(mean=weights.meta["mean"], std=weights.meta["std"]),
    ])

    # define the transformations for the testing data
    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=weights.meta["mean"], std=weights.meta["std"]),
    ])

    train_data = datasets.ImageFolder(train_dir, transform=train_transform)
    test_data = datasets.ImageFolder(test_dir, transform=test_transform)
    validation_data = datasets.ImageFolder(validation_dir, transform=test_transform)

    # prepare the data loaders
    train_loader = DataLoader(train_data, batch_size=64, shuffle=True, num_workers=8, pin_memory=True)
    test_loader = DataLoader(test_data, batch_size=64)
    validation_loader = DataLoader(validation_data, batch_size=64)

    # define number of classes
    num_classes = len(train_data.classes)
    # replace the final layer
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    # optimizer and the loss function
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # use GPU if available
    use_gpu = torch.cuda.is_available()
    if use_gpu:
        print(f"{datetime.now()}: Using GPU (cuda)")
    else:
        print(f"{datetime.now()}: Using CPU")

    device = torch.device("cuda" if use_gpu else "cpu")
    model.to(device)

    # early stopping settings
    patience = 3
    best_loss = float('inf')
    epochs_no_improve = 0
    early_stop = False

    print(f"{datetime.now()}: Starting training for {max_epochs} epochs...")

    for epoch in range(max_epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        avg_train_loss = running_loss / len(train_loader)
        print(f"{datetime.now()}: Epoch {epoch + 1}, Training Loss: {avg_train_loss:.4f}")

        # evaluate on test set for early stopping
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for inputs, labels in validation_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()

        avg_val_loss = val_loss / len(validation_loader)
        print(f"{datetime.now()}: Epoch {epoch + 1}, Validation Loss: {avg_val_loss:.4f}")

        # Check for improvement
        if avg_val_loss < best_loss:
            best_loss = avg_val_loss
            epochs_no_improve = 0
            # save the model
            print(f"{datetime.now()}: Validation loss improved, saving model...")
            torch.save(model.state_dict(), "food_or_not_food_model.pth")
            print(f"{datetime.now()}: Model saved as food_or_not_food_model.pth")
        else:
            epochs_no_improve += 1
            print(f"{datetime.now()}: No improvement for {epochs_no_improve} epoch(s)")

        if epochs_no_improve >= patience:
            print(f"{datetime.now()}: Early stopping triggered.")
            early_stop = True
            break

    # calculate accuracy of the best model
    # load the best model
    model.load_state_dict(torch.load("food_or_not_food_model.pth"))
    model.to(device)
    print(f"{datetime.now()}: Evaluating the best model on the test set...")

    model.eval()
    all_predictions = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # calculate the accuracy
    accuracy = sum([p == t for p, t in zip(all_predictions, all_labels)]) / len(all_labels)
    print(f"{datetime.now()}: Test Accuracy: {accuracy * 100:.2f}%")

    # calculate precision, recall, and F1-score
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_predictions, average="binary" if len(set(all_labels)) == 2 else "macro"
    )

    print(f"{datetime.now()}: Precision: {precision:.4f}")
    print(f"{datetime.now()}: Recall:    {recall:.4f}")
    print(f"{datetime.now()}: F1-Score:  {f1:.4f}")
