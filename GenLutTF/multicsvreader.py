import numpy as np
import pandas as pd
from tensorflow.keras.utils import Sequence


class MultiCSVReader(Sequence):
    
    def __init__(self, csv_list, csv_sizes, batch_size, csv_dtypes, x_cols, y_cols):
        self._csv_list = csv_list
        self._csv_sizes = csv_sizes
        self._batch_size = batch_size
        self._csv_dtypes = csv_dtypes
        self._x_cols = x_cols
        self._y_cols = y_cols
        
        assert len(csv_list) == len(csv_sizes)
        self._total_rows = sum(csv_sizes)
        
        self._reset()
    
    def _reset(self):
        self._currently_loaded = -1
        self._prev_index = -1
        self._prev_row_end = 0
        self._x_buffer = None
        self._y_buffer = None
    
    def __load_csv_to_buffer(self, csv_index):
        self._x_buffer = None
        self._y_buffer = None
        csv_data = pd.read_csv(self._csv_list[csv_index], dtype=self._csv_dtypes)
        self._x_buffer = csv_data[self._x_cols]
        self._y_buffer = csv_data[self._y_cols]
        self._currently_loaded = csv_index
        self._prev_row_end = 0
        csv_data = None
    
    def __load_csv_if_needed(self, batch_index):
        if self._currently_loaded == -1 or self._prev_row_end > len(self._x_buffer):
            self.__load_csv_to_buffer(self._currently_loaded + 1)
    
    def on_epoch_end(self):
        self._reset()
    
    def __getitem__(self, index):
        """
        Generates one batch of data
        :param index: the batch index
        :return: A batch of data
        """
        self.__load_csv_if_needed(index)
        
        if index != self._prev_index + 1:
            print("WARNING: must get items in sequential order")
        
        row_start = self._prev_row_end
        row_end = row_start + self._batch_size
        self._prev_row_end = row_end
        
        self._prev_index = index
        return self._x_buffer[row_start:row_end], self._y_buffer[row_start:row_end]
    
    def __len__(self) -> int:
        """
        Denotes the number of batches per epoch
        :return: the number of batches per epoch
        """
        return self._total_rows // self._batch_size
