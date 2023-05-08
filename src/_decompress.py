import gzip
import math
import subprocess
import os
import zlib
import mmap
from os.path import exists, basename, join, dirname, splitext, isfile

import numpy as np
import tifffile
from PIL import Image
from tqdm import tqdm


def decompress(input_file: str | os.PathLike, output_dir: str | os.PathLike, chunk_size=int(2**22), use_tqdm=True) -> str:
    filename = basename(input_file)
    os.makedirs(output_dir, exist_ok=True)
    filebase, ext = [splitext(filename)[0], '.tif']
    output_file = f"{join(output_dir, filebase)}_UNCOMPRESSED{ext}"

    with open(input_file, 'rb') as f_in:
        mm = mmap.mmap(f_in.fileno(), 0, access=mmap.ACCESS_READ)
        # mm_current_pos = 0
        shape = tifffile.TiffFile(f_in).pages[0].shape
        if not exists(output_file):
            with tifffile.TiffWriter(output_file, bigtiff=True) as file:
                file.write(np.zeros(shape=shape, dtype=np.uint8), shape=shape, dtype=np.dtype(np.uint8))
                pass
            pass
        with open(output_file, 'r+b') as f_out:
            out = mmap.mmap(f_out.fileno(), 0, access=mmap.ACCESS_WRITE)
            total = math.ceil((out.size() / (3*chunk_size)))
            if use_tqdm:
                for data in tqdm(iter(lambda: mm.read(chunk_size), b''), total=total, unit='chunks'):
                    out.write(data)
                    out.flush()
                    pass
                out.close()
                pass
            else:
                for data in iter(lambda: mm.read(chunk_size), b''):
                    out.write(data)
                    out.flush()
                    pass
                out.close()
                pass
        mm.close()
        pass
    return output_file


def copy(src_file_path: str | os.PathLike, dest_dir: str | os.PathLike, chunk_size=1024, use_tqdm=True) -> str:
    filename = basename(src_file_path)
    os.makedirs(dest_dir, exist_ok=True)
    if dirname(src_file_path) == dest_dir:
        filebase, ext = splitext(filename)
        filename = f'{filebase}_COPY{ext}'
    copy_file = join(dest_dir, filename)
    with open(src_file_path, 'rb') as src_file, open(copy_file, 'wb') as dest_file:
        if use_tqdm:
            with tqdm(total=os.path.getsize(src_file_path), unit='bytes') as pbar:
                while True:
                    chunk = src_file.read(chunk_size)
                    if not chunk:
                        break
                    dest_file.write(chunk)
                    pbar.update(len(chunk))
        else:
            while True:
                chunk = src_file.read(chunk_size)  # read a chunk of bytes from source file
                if not chunk:
                    break  # end of file reached
                dest_file.write(chunk)  # write chunk to destination file
    return copy_file


def copy_image(src_image: str | os.PathLike, dest: str | os.PathLike, tile_size: int | None = 1024, use_tqdm=True) -> str:
    filename = basename(src_image)
    os.makedirs(dest, exist_ok=True)
    if dirname(src_image) == dest_dir:
        filebase, ext = splitext(filename)
        filename = f'{filebase}_COPY{ext}'
    if isfile(dest):
        copy_file = dest
    else:
        copy_file = join(dest, filename)
    shape = tifffile.TiffFile(src_image).pages[0].shape
    with tifffile.TiffWriter(copy_file, bigtiff=True) as tiff:
        file.write(np.zeros(shape=shape, dtype=bool), shape=shape, dtype=bool)
    with np.memmap(src_image, dtype=np.dtype(np.uint8), mode='r', shape=shape) as src_memmap:
        with np.memmap(copy_file, dtype=np.dtype(np.uint8), mode='r+', shape=shape) as out_memmap:
            if tile_size:
                height, width = (shape[0], shape[1])
                tiles_tall = np.arange(0, height, tile_size)
                tiles_wide = np.arange(0, width, tile_size)
                tqdm_iter = np.ndindex(len(tiles_tall), len(tiles_wide))
                if use_tqdm:
                    total = len(tiles_tall) * len(tiles_wide)
                    for [y, x] in tqdm(tqdm_iter, total=total, unit='tile', desc='Copying image contents'):
                        start_height, start_width = (y * tile_size, x * tile_size)
                        end_height, end_width = (start_height + tile_size, start_width + tile_size)
                        tile = src_memmap[start_height:end_height, start_width:end_width, ...]
                        out_memmap[start_height:end_height, start_width:end_width, ...] = tile
                        pass
                    pass
                else:
                    for [y, x] in tqdm_iter:
                        start_height, start_width = (y * tile_size, x * tile_size)
                        end_height, end_width = (start_height + tile_size, start_width + tile_size)
                        tile = src_memmap[start_height:end_height, start_width:end_width, ...]
                        out_memmap[start_height:end_height, start_width:end_width, ...] = tile
                        pass
                    pass
                pass
            else:
                out_memmap[...] = src_memmap[...]
                pass
            out_memmap.flush()
            del out_memmap
        del src_memmap
        pass
    return copy_file
