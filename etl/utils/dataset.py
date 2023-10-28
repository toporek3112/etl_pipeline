from abc import ABC, abstractmethod

class Dataset(ABC):
    
    @abstractmethod
    def extract(self):
        pass

    @abstractmethod
    def transform(self):
        pass

    @abstractmethod
    def load(self):
        pass

    