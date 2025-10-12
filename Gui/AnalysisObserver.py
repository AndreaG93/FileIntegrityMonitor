from abc import ABC, abstractmethod

class AnalysisObserver(ABC):

    @abstractmethod
    def on_file_completed(self, file_path: str) -> None:
        """
        Invoked when the analysis of a file is complete.

        :param file_path: The full path to the file that has been analyzed.
        :return: None
        """
        pass