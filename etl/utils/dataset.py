from abc import ABC, abstractmethod

class Dataset(ABC):
    
    @abstractmethod
    def extract(self, data):
        pass

    @abstractmethod
    def transform(self, data):
        pass

    @abstractmethod
    def load(self, data):
        pass

    