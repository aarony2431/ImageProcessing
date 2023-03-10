import time
import traceback
from functools import partial
from multiprocessing import Pool
from os import makedirs, sep
from os.path import *
from typing import Callable

from tqdm import tqdm

from . import ImageTIFF


def processimage(func: Callable, imagepath: str, isbgr=False, out=None, hierarchy_inputDir=None, tilesize: int = 0,
                 **kwargs):
    file = basename(imagepath)
    filebase, ext = [splitext(file)[0], '.tif']
    newfile = f'{filebase}_Processed{ext}'

    if out is None or '':
        out = '~'
        pass

    if hierarchy_inputDir is not None:
        # Replace the inputDir path with the outputDir path
        imagepath_out = join(out, imagepath.replace(hierarchy_inputDir + sep, ''))

        # Get total output path
        out = dirname(imagepath_out)

        # Make all necessary directories
        if not exists(out):
            makedirs(out)
            pass
        pass

    if not exists(join(out, newfile)):
        image = ImageTIFF(imagepath, isbgr=isbgr, tilesize=tilesize)
        func(image, **kwargs)

        image.saveRGB(out, newfile, ext='')
        print(f'\'{file}\' was processed and saved as \'{basename(newfile)}\' in \'{out}\'...')
    else:
        # print(f'{n}/{total}: \'{newfile}\' already exists in \'{out}\'!')
        print(f'\'{newfile}\' already exists in \'{out}\'!')
        pass
    pass


def processimages_loop(func: Callable, imagepaths: list[str], **kwargs):
    # Loop through each image with progress bar and perform function
    for imagepath in tqdm(imagepaths, unit='img'):
        try:
            processimage(func, imagepath, **kwargs)
        except Exception as e:
            print(Exception, imagepath, e)
            print(traceback.format_exc())
        pass
    pass


def processimages_pool(func: Callable, imagepaths: list[str], processes=2, chunksize=None, aSync=False, **kwargs):
    # Create worker pools and process images with progress bar
    with Pool(processes=max(processes, 1)) as pool:
        if aSync:
            pool.starmap_async(processimage,
                               [(partial(func, **kwargs), imagepath) for imagepath in tqdm(imagepaths, unit='img')],
                               chunksize=chunksize)
        else:
            pool.starmap(processimage,
                         [(partial(func, **kwargs), imagepath) for imagepath in tqdm(imagepaths, unit='img')],
                         chunksize=chunksize)
    pass
