import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torchvision.models import resnet18, ResNet18_Weights
from torch.utils.data import DataLoader


if __name__ == "__main__":
    # food or not food dataset archive with training and testing data
    train_dir = os.path.abspath("C:/nfr/food_or_not_food_data/archive/food_data/train")
    test_dir = os.path.abspath( "C:/nfr/food_or_not_food_data/archive/food_data/test")

    # check if the directories exist and exit the program
    if not os.path.exists(train_dir):
        print(f"Training directory {train_dir} does not exist.")
        exit(1)
    if not os.path.exists(test_dir):
        print(f"Testing directory {test_dir} does not exist.")
        exit(1)

    # prepare the data transformations
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    train_data = datasets.ImageFolder(train_dir, transform=transform)
    test_data = datasets.ImageFolder(test_dir, transform=transform)

    # prepare the data loaders
    train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=32)

    # define number of classes
    num_classes = len(train_data.classes)

    # load the pre-trained ResNet18 model
    weights = ResNet18_Weights.DEFAULT
    model = resnet18(weights=weights)

    # apply the transformations from the weights
    transform = weights.transforms()
    # replace the final layer
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    # optimizer and the loss function
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # use GPU if available
    use_gpu = torch.cuda.is_available()
    if use_gpu:
        print("Using GPU")
    else:
        print("Using CPU")

    device = torch.device("cuda" if use_gpu else "cpu")
    model.to(device)

    # training
    epochs = 5
    for epoch in range(epochs):
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

        print(f"Epoch {epoch + 1}/{epochs}, Loss: {running_loss / len(train_loader):.4f}")

    # evaluation of the model
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
    print(f"Test Accuracy: {accuracy * 100:.2f}%")

    # save the model
    torch.save(model.state_dict(), "food_or_not_food_model.pth")
    print("Modell gespeichert unter food_or_not_food_model.pth")


