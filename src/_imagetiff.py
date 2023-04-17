from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from functools import partial
from os.path import join
from typing import Callable

import cv2 as cv
import dask.array as da
import dask_image.imread

import numpy as np
from PIL import Image
from osgeo import gdal

Image.MAX_IMAGE_PIXELS = None


class ImageTIFF:
    def __init__(self, path: str, isbgr=True, tilesize: int = 0, image_library: str = 'Dask'):
        self.path = path
        self.isRGB = isbgr
        self.tile = (tilesize != 0)
        if tilesize < 0:
            raise ValueError('\'tilesize\' must be an non-negative whole number!')
        if not self.tile:
            with Image.open(path) as img:
                self.image = np.array(img, dtype=np.uint8)
                pass
            pass
        else:
            # Define image library type
            self.image_library = image_library.lower()

            if image_library.lower() == 'dask':
                chunks = (tilesize, tilesize, -1)
                self.image = da.from_array(dask_image.imread.imread(path), chunks=chunks)
                pass
            elif image_library.lower() == 'pil':
                with Image.open(path) as img:
                    # Define the tile size
                    tile_size = (tilesize, tilesize)

                    # Get the size of the input image
                    img_size = img.size

                    # Calculate the number of tiles in each dimension
                    self.num_tiles = (img_size[0] // tile_size[0], img_size[1] // tile_size[1])

                    # Split the image into tiles using numpy
                    # input_array = np.array(img, dtype=np.uint8)
                    # self.image = np.array([np.array(
                    #     [input_array[j * tile_size[1]:(j + 1) * tile_size[1], i * tile_size[0]:(i + 1) * tile_size[0], :]
                    #      for i in range(self.num_tiles[0])], dtype=np.uint8) for j in range(self.num_tiles[1])])
                    self.image = np.asarray(
                        [np.asarray(
                            [np.asarray(
                                img.crop(
                                    (j * tile_size[1],
                                     i * tile_size[0],
                                     (j + 1) * tile_size[1],
                                     (i + 1) * tile_size[0])))
                                for i in range(self.num_tiles[0])
                            ], dtype=np.uint8)
                            for j in range(self.num_tiles[1])
                        ])
                pass
            elif image_library.lower() == 'gdal':
                # Open the image using GDAL
                with gdal.Open('large_image.tif') as ds:
                    pass
                # Close the dataset
                ds = None
                pass
            else:
                raise ValueError('Not a valid image library name')

        self.maxvalue = np.amax(self.image)
        if isbgr:
            self.colors = {'red': 2,
                           'green': 1,
                           'blue': 0}
        else:
            self.colors = {'red': 0,
                           'green': 1,
                           'blue': 2}
        pass

    def copyArray(self):
        return deepcopy(self.image)

    def referenceArray(self):
        return self.image

    def getChannel(self, channel: int | str):
        # The number of dimensions of the tiles (excluding the channel dimension)
        n = self.image.ndim - 1

        # Get channel number based on type of channel
        if isinstance(channel, int):
            try:
                channelnumber = channel
            except Exception as e:
                raise IndexError('Channel index out of range!')
            pass
        elif isinstance(channel, str):
            try:
                channelnumber = self.colors[channel]
            except Exception as e:
                raise IndexError('Invalid channel color name!')
            pass
        else:
            raise TypeError('\'channel\' must be an integer or string!')
        pass

        return self.image[..., channelnumber]

    # returns the shape in the order (x, y, z)
    def shape(self):
        return np.shape(self.image)

    def imshow(self, color=''):
        if color == '':
            cv.imshow('Image', self.image)
            cv.waitKey(0)
        else:
            cv.imshow('Image', ImageTIFF.getChannel(self, color))
            cv.waitKey(0)
        pass

    def collapse(self, channel: str | int = 'all'):
        # Get channel number based on type of channel
        if channel == 'all':
            final_array = np.concatenate(np.concatenate(self.image, axis=1), axis=1, dtype=np.uint8)
        elif isinstance(channel, (int, str)):
            final_array = np.concatenate(np.concatenate(self.getChannel(channel), axis=1), axis=1, dtype=np.uint8)
            pass
        else:
            raise TypeError('\'channel\' must be a valid integer or string!')

        return final_array

    def save(self, dirpath: str, name: str, channel: str | int, ext='.tif'):
        if not self.tile:
            if channel == 'all':
                Image.fromarray(self.image.astype(np.uint8)).save(join(dirpath, name) + ext)
            elif isinstance(channel, (int, str)):
                Image.fromarray(self.getChannel(channel).astype(np.uint8)).save(join(dirpath, name) + ext)
            else:
                raise TypeError('\'channel\' must be a valid integer or string!')
        else:
            if isinstance(channel, (int, str)):
                final_array = self.collapse(channel=channel)
                Image.fromarray(final_array).save(join(dirpath, name) + ext)
            else:
                raise TypeError('\'channel\' must be a valid integer or string!')
        pass

    def invert(self):
        base = np.full(self.shape(), 255, dtype='uint8')
        self.image = base - self.image
        pass

    def saveRGB(self, dirpath: str, name: str, ext='.tif'):
        self.save(dirpath, name, 'all', ext=ext)
        pass

    def map_blocks(self, func: Callable, **kwargs):
        self.image = da.map_blocks(partial(func, **kwargs), self.image)
        pass

    def saveDask(self, dirpath: str, name: str, ext='.tif'):

        pass

    def asarray(self):
        return np.asarray(self.image)

    pass
