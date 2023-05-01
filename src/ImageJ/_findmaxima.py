import os
import PIL.Image
import numpy as np
import tifffile as tiff
from scipy import ndimage


def FindMaxima(image: np.ndarray | os.PathLike | str | tiff.TiffFile | PIL.Image.Image,
               color_channel: int | str,
               tile_size: tuple[int, int] | None = None,
               noise_tolerance: int | float = 20.0,
               neighborhood_size: int = 3) -> int:
    """
    OpenCV/NumPy version of the "Find Maxima" function in ImageJ when used to get strictly the *number* of maxima.
    :param color_channel:
    :param image:
    :param tile_size:
    :param noise_tolerance:
    :param neighborhood_size:
    :return:
    """
    global data

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
        raise TypeError(f'Invalid type for param *color_channel* in ImageJ.FindMaxima: {color_channel.__class__}')

    if isinstance(image, (os.PathLike, str)):
        # Tile the image if tile_size is provided
        if tile_size:
            # Create image file link
            with tiff.TiffFile(image) as tif:
                # get the shape of the image
                shape = tif.pages[0].shape
                height, width = (shape[0], shape[1])

                # initialize the count of maxima
                num_maxima = 0

                # Get number of tiles
                tiles_tall = np.arange(0, height, tile_size[0])
                tiles_wide = np.arange(0, width, tile_size[1])

                # loop over the image in chunks
                for [y, x] in np.ndindex(len(tiles_tall), len(tiles_wide)):
                    # define tile coordinates
                    start_height, start_width = (y * tile_size[0], x * tile_size[1])
                    end_height, end_width = (start_height + tile_size[0], start_width + tile_size[1])

                    # generate tile
                    img_chunk = tif.pages[0].asarray(out='memmap', squeeze=False)[
                                start_height:end_height, start_width:end_width, channel]

                    # find local maxima using maximum filter
                    data_max = ndimage.maximum_filter(img_chunk, size=neighborhood_size, mode='constant')

                    # find maxima above a certain noise tolerance
                    threshold = np.mean(data_max) + noise_tolerance
                    maxima = (data_max == img_chunk) & (img_chunk > threshold)

                    # perform non-maximum suppression
                    footprint = np.ones((3, 3))
                    maxima = ndimage.maximum_filter(maxima, footprint=footprint) == maxima

                    # label the maxima using connected components analysis
                    labeled, chunk_num_maxima = ndimage.label(maxima)

                    # add the count of maxima in this chunk to the total count
                    num_maxima += chunk_num_maxima
                    pass
                pass
            pass
        else:
            data = ndimage.imread(image)[..., channel]
        pass
    elif isinstance(image, tiff.TiffFile):
        # Tile the image if tile_size is provided
        if tile_size:
            # get the shape of the image
            shape = image.pages[0].shape
            height, width = (shape[0], shape[1])

            # initialize the count of maxima
            num_maxima = 0

            # Get number of tiles
            tiles_tall = np.arange(0, height, tile_size[0])
            tiles_wide = np.arange(0, width, tile_size[1])

            # loop over the image in chunks
            for [y, x] in np.ndindex(len(tiles_tall), len(tiles_wide)):
                # define tile coordinates
                start_height, start_width = (y * tile_size[0], x * tile_size[1])
                end_height, end_width = (start_height + tile_size[0], start_width + tile_size[1])

                # generate tile
                img_chunk = image.pages[0].asarray(out='memmap', squeeze=False)[
                            start_height:end_height, start_width:end_width, channel]

                # find local maxima using maximum filter
                data_max = ndimage.maximum_filter(img_chunk, size=neighborhood_size, mode='constant')

                # find maxima above a certain noise tolerance
                threshold = np.mean(data_max) + noise_tolerance
                maxima = (data_max == img_chunk) & (img_chunk > threshold)

                # perform non-maximum suppression
                footprint = np.ones((3, 3))
                maxima = ndimage.maximum_filter(maxima, footprint=footprint) == maxima

                # label the maxima using connected components analysis
                labeled, chunk_num_maxima = ndimage.label(maxima)

                # add the count of maxima in this chunk to the total count
                num_maxima += chunk_num_maxima
                pass
            pass
        else:
            data = np.asarray(image.asarray())[..., channel]
            pass
        pass
    elif isinstance(image, PIL.Image.Image):
        # Tile the image if tile_size is provided
        if tile_size:
            # open image with PIL
            data = np.asarray(image)[..., channel]

            # get the shape of the image
            shape = data.shape
            height, width = (shape[0], shape[1])

            # initialize the count of maxima
            num_maxima = 0

            # Get number of tiles
            tiles_tall = np.arange(0, height, tile_size[0])
            tiles_wide = np.arange(0, width, tile_size[1])

            # loop over the image in chunks
            for [y, x] in np.ndindex(len(tiles_tall), len(tiles_wide)):
                # define tile coordinates
                start_height, start_width = (y * tile_size[0], x * tile_size[1])
                end_height, end_width = (start_height + tile_size[0], start_width + tile_size[1])

                # generate tile
                img_chunk = np.asarray(data[start_height:end_height, start_width:end_width, channel])

                # find local maxima using maximum filter
                data_max = ndimage.maximum_filter(img_chunk, size=neighborhood_size, mode='constant')

                # find maxima above a certain noise tolerance
                threshold = np.mean(data_max) + noise_tolerance
                maxima = (data_max == img_chunk) & (img_chunk > threshold)

                # perform non-maximum suppression
                footprint = np.ones((3, 3))
                maxima = ndimage.maximum_filter(maxima, footprint=footprint) == maxima

                # label the maxima using connected components analysis
                labeled, chunk_num_maxima = ndimage.label(maxima)

                # add the count of maxima in this chunk to the total count
                num_maxima += chunk_num_maxima
                pass
            pass
        else:
            data = np.asarray(image)[..., channel]
        pass
    elif not isinstance(image, np.ndarray):
        raise TypeError(f'Invalid data type for parameter *image* in ImageJ.FindMaxima: {image.__class__}')
    else:
        data = np.asarray(image)[..., channel]
        pass

    # Process separate code if input is a numpy array or if no tile_size
    if isinstance(image, np.ndarray) or tile_size:
        # find local maxima using maximum filter
        data_max = ndimage.maximum_filter(data, size=neighborhood_size, mode='constant')

        # find maxima above a certain noise tolerance
        threshold = np.mean(data_max) + noise_tolerance
        maxima = (data_max == data) & (data > threshold)

        # perform non-maximum suppression
        footprint = np.ones((3, 3))
        maxima = ndimage.maximum_filter(maxima, footprint=footprint) == maxima

        # label the maxima using connected components analysis
        labeled, num_maxima = ndimage.label(maxima)

        # return the number of maxima
        num_maxima = np.max(labeled)
    else:
        raise Exception(f'Unknown Error')
    return num_maxima
