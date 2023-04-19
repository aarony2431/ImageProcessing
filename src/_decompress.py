import gzip
import subprocess
import os
import zlib
from os.path import exists

import numpy as np
import tifffile
from PIL import Image


def decompress(input_file_path: str,
               output_dir_path: str,
               library: str = ''):
    # Create new filename
    filename = f'{os.path.splitext(os.path.basename(input_file_path))[0]}_Processed.tif'
    new_file_path = os.path.join(output_dir_path, filename)

    if library.lower() == 'gzip':
        # Open the compressed TIFF image
        im = Image.open(input_file_path)

        # Open the uncompressed TIFF image for writing
        new_im = Image.new(im.mode, im.size)
        new_im_fp = gzip.open(new_file_path, 'wb')

        # Read and decompress the image data in chunks
        chunk_size = 1024 * 1024  # 1 MB
        while True:
            data = im.fp.read(chunk_size)
            if not data:
                break
            decompressed_data = gzip.decompress(data)
            new_im_fp.write(decompressed_data)

        # Close the files
        im.fp.close()
        new_im_fp.close()

        # Save the uncompressed image to the output directory
        new_im.save(new_file_path)
        pass
    elif library.lower() == 'zlib':
        # Open the compressed TIFF image
        im = Image.open(input_file_path)

        # Open the uncompressed TIFF image for writing
        new_im = Image.new(im.mode, im.size)
        new_im_fp = open(new_file_path, 'wb')

        # Read and decompress the image data in chunks
        chunk_size = 1024 * 1024  # 1 MB
        while True:
            data = im.fp.read(chunk_size)
            if not data:
                break
            decompressed_data = zlib.decompress(data)
            new_im_fp.write(decompressed_data)

        # Close the files
        im.fp.close()
        new_im_fp.close()

        # Save the uncompressed image to the output directory
        new_im.save(new_file_path)
        pass
    elif library.lower() == 'lzw':
        with tifffile.TiffFile(input_file_path) as tif:
            uncompressed_data = tif.asarray()

        with tifffile.TiffWriter(new_file_path, bigtiff=True) as tif:
            for i in range(0, uncompressed_data.shape[0], 256):
                chunk = uncompressed_data[i:i + 256, :, :]
                tif.write(chunk)
        pass
    else:
        if not exists(new_file_path):
            with Image.open(input_file_path) as compressed_img:
                with Image.fromarray(np.asarray(compressed_img)) as uncompressed_img:
                    uncompressed_img.save(new_file_path)
                    pass
                pass
            pass
        else:
            new_file_path = None
            pass
        pass
    return new_file_path


    # # Create the output directory if it doesn't exist
    # os.makedirs(output_dir_path, exist_ok=True)
    #
    # # Get the base filename of the input file
    # filename = os.path.splitext(os.path.basename(input_file_path))[0]
    #
    # # Call tiffcp to uncompress the TIFF file in chunks
    # chunk_size = 1024 * 1024  # 1 MB
    # offset = 0
    # count = 0
    # while True:
    #     output_file_path = os.path.join(output_dir_path, f"{filename}_{count}.tif")
    #     cmd = [
    #         'tiffcp', '-c', 'none', '-o', output_file_path,
    #         input_file_path + f':{offset},{chunk_size}'
    #     ]
    #     subprocess.run(cmd, check=True)
    #
    #     # Increment the offset and count
    #     offset += chunk_size
    #     count += 1
    #
    #     # Check if we've read the entire file
    #     if offset >= os.path.getsize(input_file_path):
    #         break
    #
    # # Combine the chunks into a single file
    # output_file_path = os.path.join(output_dir_path, f"{filename}_decompressed.tif")
    # cmd = ['tiffcp', '-c', 'none', '-o', output_file_path]
    # cmd += [os.path.join(output_dir_path, f"{filename}_{i}.tif") for i in range(count)]
    # subprocess.run(cmd, check=True)
    #
    # # Delete the temporary files
    # for i in range(count):
    #     os.remove(os.path.join(output_dir_path, f"{filename}_{i}.tif"))
    pass
