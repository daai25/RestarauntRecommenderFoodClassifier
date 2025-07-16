import os
from abc import ABC, abstractmethod

class ImageFilterExtension(ABC):
    """
    Interface for image filter extension classes.
    """
    def __init__(self, verbose: bool=False):
        """
        Initialize the ImageFilterExtensionInterface with a verbosity flag.

        Args:
            verbose (bool): If True, print detailed information during processing.
        """
        self.verbose = verbose

    @abstractmethod
    def _do_filtering(self, directory: str, statistics: dict, delete: bool=True) -> dict:
        """
        Abstract method to filter images based on specific criteria.

        Args:
            directory (str): Directory path to scan for images.
            statistics (dict): A dictionary to store statistics about the filtering process.
            delete (bool): If True, delete images that do not meet the criteria directly. Default is True.
        """
        pass

    def filter_images(self, directory: str, statistics: dict, delete: bool=True) -> dict:
        """
        Scan the directory for images and apply filtering criteria.

        Args:
            directory (str): Directory path to scan for images.
            statistics (dict): A dictionary to store statistics about the filtering process.
            delete (bool): If True, delete images that do not meet the criteria directly. Default is True.
        Returns:
            A dictionary containing diverse statistics about the processed images.
        """
        # check if the directory exists
        # if os.path.exists(directory):
        #     raise FileNotFoundError(f"{self.__class__.__name__}: Directory does not exist: {directory}")

        # apply the abstract filtering method
        return self._do_filtering(directory, statistics, delete)