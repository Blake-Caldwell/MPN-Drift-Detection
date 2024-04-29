from abc import ABC, abstractmethod

class InputSource(ABC):
    def __init__(self):
        self._dataFrame = None

    @property
    def dataFrame(self):
        return self._dataFrame
    
    @dataFrame.setter
    def dataFrame(self, df):
        self._dataFrame = df
    
    @abstractmethod
    def readData(self):
        pass
