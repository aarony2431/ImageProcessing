from os import makedirs, sep
from os.path import *
from typing import Callable

from . import ImageTIFF


def processimage(func: Callable, imagepath: str, isbgr=False, out=None, hierarchy_inputDir=None, tile=False, **kwargs):
    file = basename(imagepath)
    filebase, ext = [splitext(file)[0], '.tif']
    newfile = f'{filebase}_Processed_{ext}'

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
        image = ImageTIFF(imagepath, isbgr=isbgr, tile=tile)
        func(image, **kwargs)

        image.saveRGB(out, newfile, ext='')
        print(f'\'{file}\' was processed and saved as \'{basename(newfile)}\' in \'{out}\'...')
    else:
        # print(f'{n}/{total}: \'{newfile}\' already exists in \'{out}\'!')
        print(f'\'{newfile}\' already exists in \'{out}\'!')
        pass
    pass