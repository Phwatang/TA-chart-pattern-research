# Code here is too simplify tracking and importing all data within this folder

import pandas as pd
import os 

# Absolute directory for this data folder
_data_path = os.path.dirname(os.path.realpath(__file__)) + "\\"

class Database:
    def __init__(self):
        # Iterate through the data folder and find all csv files
        self.tickers: list[str] = []
        for entry in os.scandir(_data_path):
            if entry.is_file() and entry.name[-4:] == ".csv":
                # Store csv file name without ".csv" extension
                self.tickers.append(entry.name[:-4])

    def get_ticker(self, ticker: str) -> pd.DataFrame:
        """Reads the data of the csv relating to the ticker and returns
        it as a Dataframe"""

        # Basic check
        if not ticker in self.tickers:
            raise Exception(f"ticker: {ticker} does not have any associated csv")
        # Perform read
        output = pd.read_csv(_data_path + ticker + ".csv", index_col="time")
        output.index = pd.DatetimeIndex(output.index)
        return output
