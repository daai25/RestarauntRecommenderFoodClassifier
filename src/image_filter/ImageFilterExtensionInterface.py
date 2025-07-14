from abc import ABC, abstractmethod

class ImageFilterExtensionInterface(ABC):
    """
    Interface for image filter extension classes.
    """
    @abstractmethod
    def filter_images(self, directory: str, is_relative: bool):
        """
        Scan the directory for images and apply filtering criteria.

        Args:
            directory (str): Directory path to scan for images.
            is_relative (bool): If True, the directory path is relative; otherwise, it is absolute.
        """
        pass