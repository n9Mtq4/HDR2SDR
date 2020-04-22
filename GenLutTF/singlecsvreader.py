import pandas as pd
import numpy as np
from tensorflow.keras.utils import Sequence


class SingleCSVReader(Sequence):
    
    def __init__(self, csv_file, batch_size, csv_dtypes, x_cols, y_cols):
        self._csv_file = csv_file
        self._batch_size = batch_size
        self._csv_dtypes = csv_dtypes
        self._x_cols = x_cols
        self._y_cols = y_cols
        
        self._total_rows = 0
        
        self._reset()
    
    def load(self):
        self.__load_csv_to_buffer()
        self._total_rows = len(self._x_buffer)
    
    def _reset(self):
        self._x_buffer = None
        self._y_buffer = None
    
    def __load_csv_to_buffer(self):
        self._x_buffer = None
        self._y_buffer = None
        csv_data = pd.read_csv(self._csv_file, dtype=self._csv_dtypes)
        self._x_buffer = csv_data[self._x_cols]
        self._y_buffer = csv_data[self._y_cols]
        csv_data = None
    
    def __getitem__(self, index):
        """
        Generates one batch of data
        :param index: the batch index
        :return: A batch of data
        """
        row_start = self._batch_size * index
        row_end = min(row_start + self._batch_size, self._total_rows)
        
        return np.array(self._x_buffer[row_start:row_end]), np.array(self._y_buffer[row_start:row_end])
    
    def __len__(self) -> int:
        """
        Denotes the number of batches per epoch
        :return: the number of batches per epoch
        """
        return self._total_rows // self._batch_size
