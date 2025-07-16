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

    def filter_images(self, directory: str, statistics: dict, is_relative: bool=True, delete: bool=True) -> dict:
        """
        Scan the directory for images and apply filtering criteria.

        Args:
            directory (str): Directory path to scan for images.
            statistics (dict): A dictionary to store statistics about the filtering process.
            is_relative (bool): If True, the directory path is relative; otherwise, it is absolute. Default is True.
            delete (bool): If True, delete images that do not meet the criteria directly. Default is True.
        Returns:
            A dictionary containing diverse statistics about the processed images.
        """
        # build the relative or absolute path for the directory
        if is_relative:
            directory = os.path.relpath(directory)
        else:
            directory = os.path.abspath(directory)

        # check if the directory exists
        if os.path.exists(directory):
            raise FileNotFoundError(f"Directory does not exist: {directory}")

        # apply the abstract filtering method
        return self._do_filtering(directory, statistics, delete)