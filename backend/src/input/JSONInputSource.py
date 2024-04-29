from InputSource import InputSource

import pandas as pd

class JSONInputSource(InputSource):
    def readData(self,file):
        dataFrame = pd.read_json(file)
        self.dataFrame = dataFrame
