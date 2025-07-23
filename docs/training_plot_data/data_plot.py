import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

# training and validation loss of training with base data and no augmentation
x_resnet18_base_no_aug = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
y_train_loss_resnet18_base_no_aug = np.array([0.2928, 0.2295, 0.2019, 0.1961, 0.1791, 0.1736, 0.1684, 0.1654, 0.1560, 0.1475, 0.1412])
y_val_loss_resnet18_base_no_aug = np.array([0.2132, 0.2486, 0.1996, 0.1666, 0.3214, 0.1452, 0.1500, 0.1507, 0.1455, 0.1705, 0.1888])

# training and validation loss of training with base data and augmentation
x_resnet18_base_aug = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
y_train_loss_resnet18_base_aug = np.array([0.1906, 0.1271, 0.1008, 0.0857, 0.0762, 0.0694, 0.0624, 0.0592, 0.0562, 0.0513])
y_val_loss_resnet18_base_aug = np.array([0.2062, 0.1453, 0.105, 0.1420, 0.1300, 0.1498, 0.1662, 0.1913, 0.1537, 0.1634])

# training and validation loss of training with improved data and augmentation
x_resnet18_improved_aug = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
y_train_loss_resnet18_improved_aug = np.array([0.2363, 0.1937, 0.1806, 0.1598, 0.1471, 0.1369, 0.1287, 0.1198, 0.1143])
y_val_loss_resnet18_improved_aug = np.array([0.1820, 0.4569, 0.1283, 0.1078, 0.1225, 0.1210, 0.1153, 0.1127, 0.1116])

# training and validation accuracy of training with improved data and augmentation
x_resnet50_improved_aug = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37])
y_train_accuracy_resnet50_improved_aug = np.array([0.876, 0.937, 0.946, 0.949, 0.957, 0.957, 0.961, 0.962, 0.964, 0.967, 0.966, 0.968, 0.972, 0.973, 0.973, 0.973, 0.972, 0.975, 0.976, 0.978, 0.977, 0.977, 0.978, 0.980, 0.981, 0.980, 0.981, 0.980, 0.981, 0.983, 0.983, 0.984, 0.984, 0.985, 0.985, 0.985, 0.986])
y_val_accuracy_resnet50_improved_aug = np.array([0.966, 0.974, 0.975, 0.977, 0.979, 0.979, 0.978, 0.979, 0.979, 0.981, 0.980, 0.981, 0.980, 0.981, 0.980, 0.981, 0.981, 0.982, 0.980, 0.981, 0.978, 0.983, 0.979, 0.981, 0.981, 0.981, 0.983, 0.983, 0.981, 0.983, 0.983, 0.986, 0.981, 0.983, 0.983, 0.984, 0.983])

def main():
    plt.figure(figsize=(12, 5))
    plt.plot(x_resnet18_base_no_aug, y_train_loss_resnet18_base_no_aug, label="Train Loss", marker='o')
    plt.plot(x_resnet18_base_no_aug, y_val_loss_resnet18_base_no_aug, label="Val Loss", marker='o')
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training and Validation Loss for Base Data without Augmentation (ResNet18)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 5))
    plt.plot(x_resnet18_base_aug, y_train_loss_resnet18_base_aug, label="Train Loss", marker='o')
    plt.plot(x_resnet18_base_aug, y_val_loss_resnet18_base_aug, label="Val Loss", marker='o')
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training and Validation Loss for Base Data with Augmentation (ResNet18)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 5))
    plt.plot(x_resnet18_improved_aug, y_train_loss_resnet18_improved_aug, label="Train Loss", marker='o')
    plt.plot(x_resnet18_improved_aug, y_val_loss_resnet18_improved_aug, label="Val Loss", marker='o')
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training and Validation Loss for Improved Data with Augmentation (ResNet18)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 5))
    plt.plot(x_resnet50_improved_aug, y_train_accuracy_resnet50_improved_aug, label="Train Accuracy", marker='o')
    plt.plot(x_resnet50_improved_aug, y_val_accuracy_resnet50_improved_aug, label="Val Accuracy", marker='o')
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Training and Validation Accuracy for Improved Data with Augmentation (ResNet50)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()