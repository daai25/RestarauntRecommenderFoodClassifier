import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

x_resnet50 = np.array([1, 2, 3, 4, 5, 6, 7, 8,
                       9, 10, 11, 12, 13, 14, 15, 16,
                       17, 18, 19])
y_train_accuracy_resnet50 = np.array([0.097, 0.330, 0.468, 0.550, 0.605, 0.650,
                                      0.683, 0.710, 0.734, 0.757, 0.779, 0.796,
                                      0.810, 0.820, 0.830, 0.843, 0.851, 0.860,
                                      0.864])
y_validation_accuracy_resnet50 = np.array([0.348, 0.523, 0.616, 0.669, 0.713,
                                           0.740, 0.765, 0.783, 0.796, 0.807,
                                           0.816, 0.822, 0.822, 0.827, 0.833,
                                           0.828, 0.833, 0.828, 0.833])

def main():
    plt.figure(figsize=(12, 5))
    plt.plot(x_resnet50, y_train_accuracy_resnet50,
             label="Train Accuracy", marker='o')
    plt.plot(x_resnet50, y_validation_accuracy_resnet50,
             label="Val Accuracy", marker='o')

    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title("Training and Validation Accuracy for Food Classifier (ResNet50)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
