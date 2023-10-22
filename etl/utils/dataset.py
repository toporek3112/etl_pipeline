from abc import ABC, abstractmethod

class Dataset(ABC):
    
    @abstractmethod
    def extract_and_save(self, data):
        pass
    