from abc import ABC, abstractmethod

class AbstractAlpha(ABC):
    def __init__(self):
        self.name = 'abstract_alpha'
        self.lookback = 0
        self.factor_list = []

    @abstractmethod
    def generate_day(self, day, data):
        """
        Args:
            day: index of the day (e.g., -1 for today)
            data: dict containing factor data and current state
        Returns:
            A numpy array of target weights
        """
        pass