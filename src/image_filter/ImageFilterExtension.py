from .FilterStatistics import FilterStatistics
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
    def _do_filtering(self, directory: str, statistics: FilterStatistics, delete: bool=True) -> FilterStatistics:
        """
        Abstract method to filter images based on specific criteria.

        Args:
            directory (str): Directory path to scan for images.
            statistics (FilterStatistics): A data class to store statistics about the filtering process.
            delete (bool): If True, delete images that do not meet the criteria directly. Default is True.
        Returns:
            FilterStatistics: The updated statistics including counts of filtered images, and any errors encountered.
        """
        pass

    def filter_images(self, directory: str, statistics: FilterStatistics, delete: bool=True) -> FilterStatistics:
        """
        Scan the directory for images and apply filtering criteria.

        Args:
            directory (str): Directory path to scan for images.
            statistics (FilterStatistics): A data class to store statistics about the filtering process.
            delete (bool): If True, delete images that do not meet the criteria directly. Default is True.
        Returns:
            FilterStatistics: The updated statistics including counts of filtered images, and any errors encountered.
        """
        # check if the directory exists
        # if os.path.exists(directory):
        #     raise FileNotFoundError(f"{self.__class__.__name__}: Directory does not exist: {directory}")

        # apply the abstract filtering method
        return self._do_filtering(directory, statistics, delete)