import os

import numpy as np
import tifffile as tiff


def threshold_huang(
        image: os.PathLike | str,
        threshold_channel: int | str,
        tile_size: tuple[int, int] | None = None,
        white_background: bool = True
) -> np.ndarray:
    """

    :param white_background:
    :param image:
    :param threshold_channel:
    :param tile_size:
    :return:
    """
    if isinstance(threshold_channel, str):
        colors = {
            'red': 0,
            'green': 1,
            'blue': 2
        }
        channel = colors[threshold_channel]
        pass
    elif isinstance(threshold_channel, int):
        channel = threshold_channel
        pass
    else:
        raise TypeError(f'Invalid type for param *threshold_channel* in ImageJ.threshold: {threshold_channel.__class__}')

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

        # Load the TIFF image into memory-mapped data
        mmap_data = np.memmap(image, shape=shape, mode='r')

        # loop over the image in chunks
        for [y, x] in np.ndindex(len(tiles_tall), len(tiles_wide)):
            # define tile coordinates
            start_height, start_width = (y * tile_size[0], x * tile_size[1])
            end_height, end_width = (start_height + tile_size[0], start_width + tile_size[1])

            data = mmap_data[start_height:end_height, start_width:end_width, channel]

            # apply Huang's thresholding method
            hist, bins = np.histogram(data.astype(np.uint8).ravel(), 256, [0, 256])
            hist_norm = hist.astype('float') / hist.max()

            omega = np.cumsum(hist_norm)
            mu = np.cumsum(hist_norm * np.arange(0, 256))
            mu_t = mu[-1]

            # avoid divide by zero warning
            eps = np.finfo(float).eps
            omega[omega == 0] = eps
            omega[omega == 1] = 1 - eps

            # calculate the between-class variance
            i = np.arange(0, 256)
            w0 = omega[i]
            w1 = 1 - w0
            mu_0 = mu[i] / w0
            mu_1 = (mu_t - mu[i]) / w1
            s = w0 * w1 * ((mu_0 - mu_1) ** 2)
            best_thresh = np.argmax(s)

            print(best_thresh)

            binary[start_height:end_height, start_width:end_width] = \
                data < best_thresh if white_background else data > best_thresh
            pass
        del mmap_data
        pass
    else:
        data = tiff.imread(image)[..., channel]

        # apply Huang's thresholding method
        hist, bins = np.histogram(data.astype(np.uint8).ravel(), 256, [0, 256])
        hist_norm = hist.astype('float') / hist.max()

        omega = np.cumsum(hist_norm)
        mu = np.cumsum(hist_norm * np.arange(0, 256))
        mu_t = mu[-1]

        # avoid divide by zero warning
        eps = np.finfo(float).eps
        omega[omega == 0] = eps
        omega[omega == 1] = 1 - eps

        # calculate the between-class variance
        i = np.arange(0, 256)
        w0 = omega[i]
        w1 = 1 - w0
        mu_0 = mu[i] / w0
        mu_1 = (mu_t - mu[i]) / w1
        s = w0 * w1 * ((mu_0 - mu_1) ** 2)
        best_thresh = np.argmax(s)

        binary = data < best_thresh if white_background else data > best_thresh
    return binary
