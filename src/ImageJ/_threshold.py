import os

import numpy as np
import tifffile as tiff


def threshold_huang(
        image: os.PathLike | str,
        color_channel: int | str,
        tile_size: tuple[int, int] | None = None
        ) -> np.ndarray:
    """

    :param image:
    :param color_channel:
    :param tile_size:
    :return:
    """
    if isinstance(color_channel, str):
        colors = {
            'red': 0,
            'green': 1,
            'blue': 2
        }
        channel = colors[color_channel]
        pass
    elif isinstance(color_channel, int):
        channel = color_channel
        pass
    else:
        raise TypeError(f'Invalid type for param *color_channel* in ImageJ.threshold: {color_channel.__class__}')

    # get shape of array
    shape = tiff.TiffFile(image).pages[0].shape
    if tile_size:
        # get the shape of the image
        height, width = (shape[0], shape[1])

        # generate blank output matrix
        binary = np.zeros(shape=(height, width), dtype=bool)

        # Get number of tiles
        tiles_tall = np.arange(0, height, tile_size[0])
        tiles_wide = np.arange(0, width, tile_size[1])

        # loop over the image in chunks
        for [y, x] in np.ndindex(len(tiles_tall), len(tiles_wide)):
            # define tile coordinates
            start_height, start_width = (y * tile_size[0], x * tile_size[1])
            end_height, end_width = (start_height + tile_size[0], start_width + tile_size[1])

            # Load the TIFF image into memory-mapped data
            data = np.memmap(image, shape=shape)[start_height:end_height, start_width:end_width, channel]

            # Calculate the histogram of the image
            hist, bins = np.histogram(data, bins=256)

            # Calculate the cumulative distribution function (CDF) of the histogram
            cdf = np.cumsum(hist)

            # Calculate the probabilities of the pixels belonging to the foreground and background using the CDF
            probs = hist / float(cdf[-1])

            # Calculate the entropies of the foreground and background regions for each possible threshold value
            entropies = -probs * np.log2(probs) - (1 - probs) * np.log2(1 - probs)

            # Find the threshold value that maximizes the sum of the entropies
            threshold = np.argmax(entropies)

            # Apply the threshold to the image to obtain the binary image
            binary[start_height:end_height, start_width:end_width] = data > threshold

            del data
            pass
        pass
    else:
        # Load the TIFF image into memory-mapped data
        data = np.memmap(image, shape=shape)[..., channel]

        # Calculate the histogram of the image
        hist, bins = np.histogram(data, bins=256)

        # Calculate the cumulative distribution function (CDF) of the histogram
        cdf = np.cumsum(hist)

        # Calculate the probabilities of the pixels belonging to the foreground and background using the CDF
        probs = hist / float(cdf[-1])

        # Calculate the entropies of the foreground and background regions for each possible threshold value
        entropies = -probs * np.log2(probs) - (1 - probs) * np.log2(1 - probs)

        # Find the threshold value that maximizes the sum of the entropies
        threshold = np.argmax(entropies)

        # Apply the threshold to the image to obtain the binary image
        binary = data > threshold
        del data
        pass
    return binary
