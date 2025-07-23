import torch

def setup_device() -> torch.device:
    """
    Sets up the device for PyTorch based on availability of MPS (Apple Silicon), CUDA (NVIDIA GPUs), or CPU.

    Returns:
        torch.device: The device to be used for PyTorch operations (MPS, CUDA, or CPU).
    """
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    return device

def parse_device(device: str) -> torch.device:
    """
    Parses the device string to return a corresponding torch.device object.

    Args:
        device (str): The device string, e.g., "cpu", "cuda", "mps".
    Returns:
        torch.device: The corresponding torch.device object.
    Raises:
        ValueError: If the device string is not recognized.
    """
    if device.lower() == "cpu":
        return torch.device("cpu")
    elif device.lower() == "cuda":
        return torch.device("cuda")
    elif device.lower() == "mps":
        return torch.device("mps")
    else:
        raise ValueError(f"Unsupported device: {device}")

