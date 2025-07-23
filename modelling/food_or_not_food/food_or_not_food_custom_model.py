import torch.nn as nn


class SimpleCNN(nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()
        self.features = nn.Sequential(
            # Input: 3×224×224
            nn.Conv2d(3, 32, kernel_size=3, padding=1),  # → 32×224×224
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # → 32×112×112
            nn.Conv2d(32, 64, kernel_size=3, padding=1),  # → 64×112×112
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # → 64×56×56
            nn.Conv2d(64, 128, kernel_size=3, padding=1),  # → 128×56×56
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # → 128×28×28
            nn.Conv2d(128, 256, kernel_size=3, padding=1),  # → 256×28×28
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # → 256×14×14
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),  # → 128*28*28
            nn.Linear(256 * 14 * 14, 256),  # Fully connected layer
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x
