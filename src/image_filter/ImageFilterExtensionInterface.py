from abc import ABC, abstractmethod

class ImageFilterExtensionInterface(ABC):
    """
    Interface for image filter extension classes.
    """
    @abstractmethod
    def filter_images(self, directory: str, is_relative: bool, delete: bool) -> dict:
        """
        Scan the directory for images and apply filtering criteria.

        Args:
            directory (str): Directory path to scan for images.
            is_relative (bool): If True, the directory path is relative; otherwise, it is absolute.
            delete (bool): If True, delete images that do not meet the criteria directly.
        Returns:
            A dictionary containing diverse statistics about the processed images.
        """
        pass