import gc
import itertools
import shutil
import struct
import time
import traceback

import numpy as np
import tifffile
from functools import partial
from multiprocessing import Pool
from os import makedirs, sep
from os.path import *
from typing import Callable, Optional

from tqdm import tqdm

from ._imagetiff import ImageTIFF
from ._decompress import decompress


def processimage(func: Callable,
                 imagepath: str,
                 isbgr=False,
                 out=None,
                 hierarchy_inputDir=None,
                 tilesize: int = 0,
                 image_library: str = 'memmap',
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
        makedirs(out, exist_ok=True)
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
                tqdm.write(f'memory/struct error: {file}')
                return imagepath
        elif image_library.lower() == 'dask':
            try:
                img = ImageTIFF(imagepath, isbgr=isbgr, tilesize=tilesize, image_library=image_library)
                img.map_blocks(func, **kwargs)
                img.saveDask(out, newfile, ext='')
                return None
            except (MemoryError, struct.error) as err:
                tqdm.write(f'memory/struct error: {file}')
                return imagepath
        elif image_library.lower() == 'tifffile':
            try:
                # Open the input TIFF file and read its dimensions
                with tifffile.TiffFile(imagepath) as tif:
                    width, height = tif.asarray().shape[-2:]

                    # Define the tile size
                    tile_width, tile_height = (256, 256)

                    # Get number of tiles
                    tiles_wide = range(0, width, tile_width)
                    tiles_tall = range(0, height, tile_height)

                    # Define output filename
                    out_file = join(out, newfile)

                    # Create an output TIFF file
                    with tifffile.TiffWriter(out_file, bigtiff=True) as out_tif:
                        # Loop over the tiles of the input file
                        tqdm_iter = itertools.product(tiles_wide, tiles_tall)
                        total = len(tiles_wide) * len(tiles_tall)
                        for (start_width, start_height) in tqdm(tqdm_iter,
                                                                total=total,
                                                                unit='tile',
                                                                desc='Progress bar for image'):
                            # Get tile
                            tile = tif.asarray()[
                                   start_width:(start_width + tile_width),
                                   start_height:(start_height + tile_height),
                                   ...]

                            # Process the tile
                            processed_tile = func(tile, **kwargs)

                            # Write the processed tile to the output file
                            out_tif.write(processed_tile, tile=(start_width, start_height))
                    return None
                pass
            except (MemoryError, struct.error) as err:
                tqdm.write(f'memory/struct error: {file}')
                return imagepath
        elif image_library.lower() == 'memmap_slow':
            # Slow but tries to lower the amount of memory usage
            try:
                # Copy and decompress file to output directory for modification
                out_file = decompress(imagepath, out, library='')

                # Open the input file and read its dimensions
                with tifffile.TiffFile(out_file) as tif:
                    shape = tif.asarray().shape
                height, width = (shape[0], shape[1])

                # Define the tile size
                tile_height, tile_width = (256, 256)

                # Get number of tiles
                tiles_tall = np.arange(0, height, tile_height)
                tiles_wide = np.arange(0, width, tile_width)

                # Iterate over each tile
                tqdm_iter = np.ndindex(len(tiles_tall), len(tiles_wide))
                total = len(tiles_tall) * len(tiles_wide)
                for [y, x] in tqdm(tqdm_iter,
                                   total=total,
                                   unit='tile',
                                   desc='Progress bar for image',
                                   leave=False,
                                   position=1):
                    start_height, start_width = (y * tile_height, x * tile_width)
                    # Load specific tile into memmap memory
                    tile = tifffile.memmap(out_file, mode='r+', dtype=np.uint8)[
                           start_height:(start_height + tile_width),
                           start_width:(start_width + tile_height),
                           ...]

                    # Process the tile and set it as the value for the new tile
                    tile_result = func(tile, **kwargs)

                    # Process the tile and set it as the value for the new tile
                    tile[...] = tile_result

                    # Delete and flush the new image
                    tile.flush()
                    del tile
                    gc.collect()
                    pass
                return None
            except (MemoryError, struct.error) as err:
                tqdm.write(f'memory/struct error: {file}')
                return imagepath
        elif image_library.lower() == 'memmap_fast':
            # Slow but tries to lower the amount of memory usage
            try:
                # Copy and decompress file to output directory for modification
                out_file = decompress(imagepath, out, library='')

                image = tifffile.memmap(out_file, mode='r+', dtype=np.uint8)
                shape = np.shape(image)
                height, width = (shape[0], shape[1])

                # Define the tile size
                tile_height, tile_width = (1024, 1024)

                # Get number of tiles
                tiles_tall = np.arange(0, height, tile_height)
                tiles_wide = np.arange(0, width, tile_width)

                # Iterate over each tile
                tqdm_iter = np.ndindex(len(tiles_tall), len(tiles_wide))
                total = len(tiles_tall) * len(tiles_wide)
                for [y, x] in tqdm(tqdm_iter,
                                   total=total,
                                   unit='tile',
                                   desc='Progress bar for image',
                                   leave=False,
                                   position=1):
                    start_height, start_width = (y * tile_height, x * tile_width)

                    # Process the tile and set it as the value for the new tile
                    tile_result = func(image[
                                       start_height:(start_height + tile_width),
                                       start_width:(start_width + tile_height),
                                       ...], **kwargs)

                    # Process the tile and set it as the value for the new tile
                    image[
                        start_height:(start_height + tile_width),
                        start_width:(start_width + tile_height),
                        ...] = tile_result
                    pass
                image.flush()
                del image
                gc.collect()
                return None
            except (MemoryError, struct.error) as err:
                tqdm.write(f'memory/struct error: {file}')
                return imagepath
        else:
            raise ValueError('Not a valid image library name')
    else:
        # print(f'{n}/{total}: \'{newfile}\' already exists in \'{out}\'!')
        tqdm.write(f'\'{newfile}\' already exists in \'{out}\'!')
        return None
    pass


def processimages_loop(func: Callable,
                       imagepaths: list[str],
                       logdir=Optional[str],
                       **kwargs):
    if logdir:
        logname = f'log{time.time_ns()}.txt'
        # with open(join(logdir, logname), 'w') as f:
        #     pass
        # Loop through each image with progress bar and perform function
        for imagepath in tqdm(imagepaths, unit='img', desc='Progress bar for process', position=0):
            try:
                out = processimage(func, imagepath, **kwargs)
                if out is not None:
                    with open(join(logdir, logname), 'a') as logfile:
                        logfile.write(out)
                        logfile.write('\n')
                    pass
            except Exception as e:
                tqdm.write(f'{Exception} {imagepath} {e}')
                tqdm.write(traceback.format_exc())
            pass
        pass
    else:
        # Loop through each image with progress bar and perform function
        for imagepath in tqdm(imagepaths, unit='img', desc='Progress bar for process', position=0):
            try:
                processimage(func, imagepath, **kwargs)
            except Exception as e:
                tqdm.write(f'{Exception} {imagepath} {e}')
                tqdm.write(traceback.format_exc())
            pass
        pass
    pass


def processimages_pool(func: Callable,
                       imagepaths: list[str],
                       processes=2,
                       chunksize=None,
                       aSync=False,
                       logdir=Optional[str],
                       **kwargs):
    if logdir:
        logname = f'log{time.time_ns()}.txt'
        # with open(join(logdir, logname), 'w') as f:
        #     pass
        with Pool(processes=max(processes, 1)) as pool:
            if aSync:
                errs = pool.starmap_async(processimage,
                                          [(partial(func, **kwargs), imagepath) for imagepath in
                                           tqdm(imagepaths, unit='img', desc='Progress bar for process', position=0)],
                                          chunksize=chunksize)
                for err in errs.get():
                    if err is not None:
                        with open(join(logdir, logname), 'a') as logfile:
                            logfile.write(err)
                            logfile.write('\n')
                            pass
                        pass
            else:
                for err in pool.starmap(processimage,
                                        [(partial(func, **kwargs), imagepath) for imagepath in
                                         tqdm(imagepaths, unit='img', desc='Progress bar for process', position=0)],
                                        chunksize=chunksize):
                    if err is not None:
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
                                   [(partial(func, **kwargs), imagepath)
                                    for imagepath in tqdm(imagepaths,
                                                          unit='img',
                                                          desc='Progress bar for process',
                                                          position=0)],
                                   chunksize=chunksize)
            else:
                pool.starmap(processimage,
                             [(partial(func, **kwargs), imagepath)
                              for imagepath in tqdm(imagepaths,
                                                    unit='img',
                                                    desc='Progress bar for process',
                                                    position=0)],
                             chunksize=chunksize)
            pass
        pass
    pass
