from typing import Tuple

import OpenImageIO as oiio

from tensorflow.keras.utils import Sequence


class HDR2SDRImageGenerator(Sequence):
    """
    A keras Sequence that generates data to train a model to create a LUT to convert HDR to SDR
    """
    
    def __init__(self, image_map, image_size, batch_size, crop=(0, 0, 0, 0)):
        """
        HDR to SDR Image Generator for keras
        :param image_map: a list of tuples of file paths. (hdr path, sdr path)
        :param image_size: a tuple of (width, height)
        :param batch_size: the batch size in pixels
        :param crop: pixels to crop (left, right, top, bottom)
        """
        self._image_map = image_map
        self._image_size = image_size
        self._batch_size = batch_size
        self._crop = crop
        
        self._pixels_per_image = self.__calc_pixels_per_image()
        assert self._pixels_per_image % batch_size == 0
        self._batches_per_image = self._pixels_per_image // batch_size
        
        self._hdr_buffer = None
        self._sdr_buffer = None
    
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
    
    def __load_buffer_if_needed(self, index) -> None:
        """
        Loads the next image into the buffer if needed
        :param index: the batch index
        :return: None
        """
        if index % self._batches_per_image != 0:
            return
        
        image_index = index // self._batches_per_image
        hdr_filepath, sdr_filepath = self._image_map[image_index]
        
        # load the buffers
        hdr_img = oiio.ImageInput.open(hdr_filepath)
        self._hdr_buffer = hdr_img.read_image(format='uint16')
        sdr_img = oiio.ImageInput.open(sdr_filepath)
        self._sdr_buffer = sdr_img.read_image(format='uint8')
        
        # crop
        left, right, top, bottom = self._crop
        width, height = self._image_size
        x_end, y_end = (width - right, height - bottom)
        self._hdr_buffer = self._hdr_buffer[top:y_end, left:x_end].reshape((self.__calc_pixels_per_image(), 3))
        self._sdr_buffer = self._sdr_buffer[top:y_end, left:x_end].reshape((self.__calc_pixels_per_image(), 3))
    
    def __getitem__(self, index):
        """
        Generates one batch of data
        :param index: the batch index
        :return: A batch of data
        """
        self.__load_buffer_if_needed(index)
        buffer_index = index % self._batches_per_image
        pixel_start = self._batch_size * buffer_index
        pixel_end = pixel_start + self._batch_size
        
        return self._hdr_buffer[pixel_start:pixel_end], self._sdr_buffer[pixel_start:pixel_end]
    
    def __len__(self) -> int:
        """
        Denotes the number of batches per epoch
        :return: the number of batches per epoch
        """
        return len(self._image_map) * self._batches_per_image

