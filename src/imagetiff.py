from copy import deepcopy
from os.path import join
import cv2 as cv

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


class ImageTIFF:
    def __init__(self, path: str, isbgr=True):
        self.path = path
        self.isRGB = isbgr
        # self.image = io.imread(self.path).astype(np.uint8)
        self.image = np.array(Image.open(path), dtype=np.uint8)
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
        if channelnumber != -1:
            return self.image[:, :, channelnumber]
        elif channelcolor != '':
            return self.image[:, :, self.colors[channelcolor]]
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
        if channel != -1:
            # io.imsave(join(dirpath, name) + ext, self.image[:, :, channel])
            Image.fromarray(self.image[:, :, channel]).save(join(dirpath, name) + ext)
        elif channelcolor != '':
            # io.imsave(join(dirpath, name) + ext, self.image[:, :, self.colors[channelcolor]])
            Image.fromarray(self.image[:, :, self.colors[channelcolor]]).save(join(dirpath, name) + ext)
        else:
            # io.imsave(join(dirpath, name) + ext, self.image)
            Image.fromarray(self.image).save(join(dirpath, name) + ext)
        pass

    def invert(self):
        base = np.full(self.shape(), 255, dtype='uint8')
        self.image = base - self.image
        pass

    def saveRGB(self, dirpath: str, name: str, ext='.tif'):
        Image.fromarray(self.image).save(join(dirpath, name) + ext)
        pass

    pass
