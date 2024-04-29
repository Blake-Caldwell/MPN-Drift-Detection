from InputSource import InputSource

import pandas as pd

class CSVInputSource(InputSource):
    def readData(self,file):
        dataFrame = pd.read_csv(file)
        return dataFrame
