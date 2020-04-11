from typing import Tuple

import cv2

import numpy as np
from tensorflow.keras.utils import Sequence


class HDR2SDRImageGenerator(Sequence):
    """
    A keras Sequence that generates data to train a model to create a LUT to convert HDR to SDR
    """
    
    def __init__(self, image_map, image_size, batch_size, crop=(0, 0, 0, 0), buffer_size=64):
        """
        HDR to SDR Image Generator for keras
        :param image_map: a list of tuples of file paths. (hdr path, sdr path)
        :param image_size: a tuple of (width, height)
        :param batch_size: the batch size in pixels
        :param crop: pixels to crop (left, right, top, bottom)
        :param buffer_size: The number of images to keep in memory
        """
        self._image_map = image_map
        self._image_size = image_size
        self._batch_size = batch_size
        self._crop = crop
        self._buffer_size = buffer_size
        
        self._pixels_per_image = self.__calc_pixels_per_image()
        assert self._pixels_per_image % batch_size == 0
        self._batches_per_image = self._pixels_per_image // batch_size
        
        self._hdr_buffer = np.zeros((self.__get_pixel_buffer_size(), 3))
        self._sdr_buffer = np.zeros((self.__get_pixel_buffer_size(), 3))
        
        self._current_buffer_range = None
    
    def __cropped_image_size(self) -> Tuple[int, int]:
        """
        Gets the true size of the image factoring pixels that are cropped out
        :rtype: Tuple[int, int]
        :return: The width, height of a cropped image
        """
        width, height = self._image_size
        x1, x2, y1, y2 = self._crop
        return (width - x1 - x2), (height - y1 - y2)
    
    def __calc_pixels_per_image(self) -> int:
        """
        Gets the number of pixels in an image factoring pixels that are cropped out
        :return: The number of pixels in a cropped image
        """
        cwidth, cheight = self.__cropped_image_size()
        return cwidth * cheight
    
    def __get_pixel_buffer_size(self):
        return self._pixels_per_image * self._buffer_size
    
    def __load_buffer_if_needed(self, index) -> None:
        """
        Loads the next image into the buffer if needed
        :param index: the batch index
        :return: None
        """
        if index % (self._batches_per_image * self._buffer_size) != 0:
            return
        
        # crop math
        left, right, top, bottom = self._crop
        width, height = self._image_size
        x_end, y_end = (width - right, height - bottom)
        
        image_start_index = index // self._batches_per_image
        image_end_index = min(image_start_index + self._buffer_size, len(self._image_map) - 1)  # range cap
        self._current_buffer_range = range(image_start_index, image_end_index)
        for image_index in range(image_start_index, image_end_index):
            
            hdr_filepath, sdr_filepath = self._image_map[image_index]
            
            # load the pixels
            hdr_pix = cv2.imread(hdr_filepath, cv2.IMREAD_UNCHANGED)[top:y_end, left:x_end].reshape((self.__calc_pixels_per_image(), 3))
            sdr_pix = cv2.imread(sdr_filepath, cv2.IMREAD_UNCHANGED)[top:y_end, left:x_end].reshape((self.__calc_pixels_per_image(), 3))
            
            # copy into the buffers
            pixel_start_index = (image_index - image_start_index) * self._pixels_per_image
            pixel_end_index = pixel_start_index + self._pixels_per_image
            self._hdr_buffer[pixel_start_index:pixel_end_index] = hdr_pix
            self._sdr_buffer[pixel_start_index:pixel_end_index] = sdr_pix
        
        # shuffle the buffer
        np.random.shuffle(self._hdr_buffer)
        np.random.shuffle(self._sdr_buffer)
    
    def __getitem__(self, index):
        """
        Generates one batch of data
        :param index: the batch index
        :return: A batch of data
        """
        self.__load_buffer_if_needed(index)
        buffer_index = index % (self._batches_per_image * self._buffer_size)
        pixel_start = self._batch_size * buffer_index
        pixel_end = pixel_start + self._batch_size
        
        # by default model.fit shuffles, so getitem isn't sequential numbers, messes up buffering. this detects that
        request_image = index // self._batches_per_image
        if request_image not in self._current_buffer_range:
            print(f"WARNING: IMAGE {request_image} IS NOT CURRENTLY IN THE BUFFER: {self._current_buffer_range}")
        
        return self._hdr_buffer[pixel_start:pixel_end], self._sdr_buffer[pixel_start:pixel_end]
    
    def __len__(self) -> int:
        """
        Denotes the number of batches per epoch
        :return: the number of batches per epoch
        """
        return len(self._image_map) * self._batches_per_image

