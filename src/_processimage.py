import struct
import time
import traceback
from functools import partial
from multiprocessing import Pool
from os import makedirs, sep
from os.path import *
from typing import Callable

from tqdm import tqdm

from . import ImageTIFF


def processimage(func: Callable,
                 imagepath: str,
                 isbgr=False,
                 out=None,
                 hierarchy_inputDir=None,
                 tilesize: int = 0,
                 image_library: str = 'dask',
                 **kwargs):
    file = basename(imagepath)
    filebase, ext = [splitext(file)[0], '.tif']
    newfile = f'{filebase}_Processed{ext}'

    if out is None or '':
        out = '~'
        pass

    if hierarchy_inputDir:
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
        if image_library.lower() == 'pil':
            try:
                img = ImageTIFF(imagepath, isbgr=isbgr, tilesize=tilesize, image_library=image_library)
                func(img, **kwargs)

                img.saveRGB(out, newfile, ext='')
                print(f'\'{file}\' was processed and saved as \'{basename(newfile)}\' in \'{out}\'...')
                return None
            except (MemoryError, struct.error) as err:
                print(f'memory/struct error: {file}')
                return imagepath
        elif image_library.lower() == 'dask':
            try:
                img = ImageTIFF(imagepath, isbgr=isbgr, tilesize=tilesize, image_library=image_library)
                img.map_blocks(func, **kwargs)
                img.saveDask(out, newfile, ext='')
                return None
            except (MemoryError, struct.error) as err:
                print(f'memory/struct error: {file}')
                return imagepath
        else:
            raise ValueError('Not a valid image library name')
    else:
        # print(f'{n}/{total}: \'{newfile}\' already exists in \'{out}\'!')
        print(f'\'{newfile}\' already exists in \'{out}\'!')
        return None
    pass


def processimages_loop(func: Callable,
                       imagepaths: list[str],
                       logdir=None,
                       **kwargs):
    if logdir:
        logname = f'log{time.time()}.txt'
        with open(join(logdir, logname), 'w') as f:
            pass
        # Loop through each image with progress bar and perform function
        for imagepath in tqdm(imagepaths, unit='img'):
            try:
                out = processimage(func, imagepath, **kwargs)
                if out is None:
                    with open(join(logdir, logname), 'a') as logfile:
                        logfile.write(out)
                    pass
            except Exception as e:
                print(Exception, imagepath, e)
                print(traceback.format_exc())
            pass
        pass
    else:
        # Loop through each image with progress bar and perform function
        for imagepath in tqdm(imagepaths, unit='img'):
            try:
                processimage(func, imagepath, **kwargs)
            except Exception as e:
                print(Exception, imagepath, e)
                print(traceback.format_exc())
            pass
        pass
    pass


def processimages_pool(func: Callable,
                       imagepaths: list[str],
                       processes=2,
                       chunksize=None,
                       aSync=False,
                       logdir=None,
                       **kwargs):
    if logdir:
        logname = f'log{time.time_ns()}.txt'
        with open(join(logdir, logname), 'w') as f:
            pass
        with Pool(processes=max(processes, 1)) as pool:
            if aSync:
                errs = pool.starmap_async(processimage,
                                          [(partial(func, **kwargs), imagepath) for imagepath in
                                           tqdm(imagepaths, unit='img')],
                                          chunksize=chunksize)
                for err in errs.get():
                    if err is None:
                        with open(join(logdir, logname), 'a') as logfile:
                            logfile.write(err)
                            pass
                        pass
            else:
                for err in pool.starmap(processimage,
                                        [(partial(func, **kwargs), imagepath) for imagepath in
                                         tqdm(imagepaths, unit='img')],
                                        chunksize=chunksize):
                    if err is None:
                        with open(join(logdir, logname), 'a') as logfile:
                            logfile.write(err)
                            pass
                        pass
            pass
        pass
    else:
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
        pass
    pass
