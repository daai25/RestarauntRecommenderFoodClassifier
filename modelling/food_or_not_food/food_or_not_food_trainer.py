import os
import argparse
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torchvision.models import resnet18, ResNet18_Weights
from torch.utils.data import DataLoader

# command line example:
# python food_or_not_food_trainer.py --train_dir C:/nfr/food_or_not_food_data/archive/food_data/train --test_dir C:/nfr/food_or_not_food_data/archive/food_data/test

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a model to classify food or not food images.")
    parser.add_argument("--train_dir", type=str, required=True, help="Path to the training data directory")
    parser.add_argument("--test_dir", type=str, required=True, help="Path to the testing data directory")
    parser.add_argument("--max_epochs", type=int, required=False, help="Number of epochs to train")
    args = parser.parse_args()

    # food or not food dataset archive with training and testing data
    train_dir = os.path.abspath(args.train_dir)
    test_dir = os.path.abspath(args.test_dir)

    # get max_epochs from command line argument or set default
    max_epochs = args.max_epochs if args.max_epochs else 30

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

    # get the transformations from the weights
    transform = weights.transforms()

    train_data = datasets.ImageFolder(train_dir, transform=transform)
    test_data = datasets.ImageFolder(test_dir, transform=transform)

    # prepare the data loaders
    train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=32)

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
        print(f"{datetime.now()}: using GPU (cuda)")
    else:
        print(f"{datetime.now()}: using CPU")

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
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()

        avg_val_loss = val_loss / len(test_loader)
        print(f"{datetime.now()}: Epoch {epoch + 1}, Validation Loss: {avg_val_loss:.4f}")

        # Check for improvement
        if avg_val_loss < best_loss:
            best_loss = avg_val_loss
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            print(f"{datetime.now()}: No improvement for {epochs_no_improve} epoch(s)")

        if epochs_no_improve >= patience:
            print(f"{datetime.now()}: Early stopping triggered.")
            early_stop = True
            break

    # calculate accuracy on the test set, with the best model
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total
    print(f"{datetime.now()}: Test Accuracy: {accuracy * 100:.2f}%")

    # save the model
    torch.save(model.state_dict(), "food_or_not_food_model.pth")
    print(f"{datetime.now()}: Model saved to food_or_not_food_model.pth")


