from copy import deepcopy
from os.path import join
import cv2 as cv

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


class ImageTIFF:
    def __init__(self, path: str, isbgr=True, tile=False):
        self.path = path
        self.isRGB = isbgr
        self.tile = tile
        if not tile:
            with Image.open(path) as img:
                self.image = np.array(img, dtype=np.uint8)
                pass
            pass
        else:
            with Image.open(path) as img:
                # Define the tile size
                tile_size = (256, 256)

                # Get the size of the input image
                img_size = img.size

                # Calculate the number of tiles in each dimension
                num_tiles = (img_size[0] // tile_size[0], img_size[1] // tile_size[1])

                # Split the image into tiles using numpy
                input_array = np.array(img)
                self.image = np.array([np.array(
                    [input_array[j * tile_size[1]:(j + 1) * tile_size[1], i * tile_size[0]:(i + 1) * tile_size[0], :]
                     for i in range(num_tiles[0])]) for j in range(num_tiles[1])])

            pass
        self.maxvalue = np.max(self.image)
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

    def getChannel(self, channelcolor='', channelnumber=-1):
        if not self.tile:
            if channelnumber != -1:
                return self.image[:, :, channelnumber]
            elif channelcolor != '':
                return self.image[:, :, self.colors[channelcolor]]
            else:
                raise NotImplementedError('Please specify a value for \'channelcolor\' or \'channelnumber\'')
        else:
            if channelnumber != -1:
                return np.array([tile[:, :, channelnumber] for tile in self.image])
            elif channelcolor != '':
                return np.array([tile[:, :, self.colors[channelcolor]] for tile in self.image])
            else:
                raise NotImplementedError('Please specify a value for \'channelcolor\' or \'channelnumber\'')

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

    def save(self, dirpath: str, name: str, ext='.tif', channel=-1, channelcolor=''):
        if not self.tile:
            if channel != -1:
                Image.fromarray(self.image[:, :, channel]).save(join(dirpath, name) + ext)
            elif channelcolor != '':
                Image.fromarray(self.image[:, :, self.colors[channelcolor]]).save(join(dirpath, name) + ext)
            else:
                Image.fromarray(self.image).save(join(dirpath, name) + ext)
            pass
        else:
            if channel != -1:
                final_array = np.concatenate(np.concatenate(self.image[:, :, channel], axis=2), axis=0)
                Image.fromarray(final_array).save(join(dirpath, name) + ext)
            elif channelcolor != '':
                final_array = np.concatenate(np.concatenate(self.image[:, :, self.colors[channelcolor]], axis=2), axis=0)
                Image.fromarray(final_array).save(join(dirpath, name) + ext)
            else:
                final_array = np.concatenate(np.concatenate(self.image, axis=2), axis=0)
                Image.fromarray(final_array).save(join(dirpath, name) + ext)
            pass

    def invert(self):
        base = np.full(self.shape(), 255, dtype='uint8')
        self.image = base - self.image
        pass

    def saveRGB(self, dirpath: str, name: str, ext='.tif'):
        self.save(dirpath, name, ext=ext)
        pass

    pass
