# src/resnet_loader/resnet18_loader.py
import os
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import resnet18, ResNet18_Weights

from .device import setup_device, parse_device

def load_resnet18_model(model_path: str, device: str=None, out_features: int=2) -> tuple[nn.Module, torch.device, transforms.Compose]:
    """
    Load a pre-trained ResNet18 model from a specified path and prepare it for inference.

    Args:
        model_path (str): Path to the pre-trained ResNet18 model file.
        device (str, optional): Device to load the model onto ('cpu', 'cuda', or 'mps'). Defaults to None, which uses the best available device.
        out_features (int): Number of output features for the final layer. Defaults to 2 (binary classification).
    Returns:
        tuple: A tuple containing the loaded model, the device, and the transformation pipeline.
    Raises:
        FileNotFoundError: If the model file does not exist at the specified path.
        ValueError: If out_features is not a positive integer.
    """

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    if out_features <= 0:
        raise ValueError("out_features must be a positive integer.")

    # set up the device if not provided
    if device is None:
        device = setup_device()
    else:
        device = parse_device(device)

    weights = ResNet18_Weights.DEFAULT
    # load the pre-trained ResNet18 model
    model = resnet18(weights=None)

    model.fc = nn.Linear(
        in_features=int(model.fc.in_features),
        out_features=out_features
    )

    # load the model state dictionary from the specified path
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    # build the transformation pipeline
    default_mean = weights.transforms().mean
    default_std = weights.transforms().std

    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=default_mean, std=default_std),
    ])

    return model, device, transform