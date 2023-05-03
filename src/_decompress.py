import gzip
import math
import subprocess
import os
import zlib
import mmap
from os.path import exists, basename, join, dirname, splitext

import numpy as np
import tifffile
from PIL import Image
from tqdm import tqdm


def decompress(input_file: str, output_dir: str, chunk_size=int(2**22), use_tqdm=True):
    filename = basename(input_file)
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


def copy(src_file_path: str, dest_dir: str, chunk_size=1024, use_tqdm=True):
    filename = basename(src_file_path)
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
