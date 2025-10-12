from abc import ABC, abstractmethod

class AnalysisLogger(ABC):

    @abstractmethod
    def log(self, message: str) -> None:
        """
        Logs a message related to the analysis process.

        :param message: The message string to be recorded.
        :return: None
        """
        pass