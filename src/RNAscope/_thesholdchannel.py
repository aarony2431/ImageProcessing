import numpy as np

from .. import ImageTIFF


def thresholdchannel(img: ImageTIFF, mainchannel='red', C2channel='green', C3channel='blue', whitebackground=True):
    """
    Thresholds the corresponding channel color and returns an image with the thresholded channel above background
    according to whitebackground. Performs the operation faster due to NumPy's broadcasting features.
    :param img:
    :param mainchannel: usually red
    :param C2channel: usually green
    :param C3channel: usually blue
    :param whitebackground: True if background colors are brighter than signal colors
    :return:
    """

    # function to decide if red color is dominant
    def redish(r, g, b):
        # Global color cutoff so that pixels are not too dark
        cutoff = np.uint(85)

        # Create cutoff mask for later faster processing
        red_mask = r > cutoff

        def isnotred_greencorrection(red, green, blue, mask):
            c1factor = 1
            c2factor = 1.15
            condition2 = green[mask] > cutoff
            condition3 = blue[mask] > cutoff
            condition4 = red[mask] > green[mask] * c1factor
            condition5 = green[mask] > blue[mask] * c2factor

            result = np.zeros_like(red, dtype=bool)
            result[mask] = np.logical_and.reduce([condition2, condition3, condition4, condition5])
            return result

        def isred_bluecorrection(red, green, blue, mask):
            green_factor = 1.1
            red_blue_offset_ratio = 0.15
            red_blue_max = np.maximum(red[mask], blue[mask])
            condition2 = red[mask] > green[mask] * green_factor
            condition3 = red[mask] > blue[mask] * green_factor
            condition4 = 1 - (red[mask] / red_blue_max) <= red_blue_offset_ratio
            condition5 = 1 - (blue[mask] / red_blue_max) <= red_blue_offset_ratio

            result = np.zeros_like(red, dtype=bool)
            result[mask] = np.logical_and.reduce([condition2, condition3, condition4, condition5])
            return result

        def isred(red, green, blue, mask):
            factor1 = 1.3
            factor2 = 1.15
            mean_offset_ratio = 0.15

            # Calculate mean and differences from mean
            mean = np.mean(np.stack((green[mask], blue[mask]), axis=-1), axis=-1)
            green_diff = np.abs(green[mask] - mean)
            blue_diff = np.abs(blue[mask] - mean)

            red_green_condition = np.logical_and(red[mask] > green[mask] * factor1,
                                                 red[mask] > blue[mask] * factor1)
            red_offset_condition = np.logical_and.reduce([green_diff < mean * mean_offset_ratio,
                                                          blue_diff < mean * mean_offset_ratio,
                                                          red[mask] > green[mask] * factor2,
                                                          red[mask] > blue[mask] * factor2])

            result = np.zeros_like(red, dtype=bool)
            result[mask] = np.logical_or(red_green_condition, red_offset_condition)
            return result

        # Logical processing to determine if color is red
        return np.logical_and(np.logical_not(isnotred_greencorrection(r, g, b, red_mask)),
                              np.logical_or(isred(r, g, b, red_mask), isred_bluecorrection(r, g, b, red_mask)))

    channel = img.getChannel(mainchannel)
    channel2 = img.getChannel(C2channel)
    channel3 = img.getChannel(C3channel)
    # Generate the new red image/tiles data
    if whitebackground:
        new_red = np.where(redish(channel, channel2, channel3),
                           np.uint8(255) - channel,
                           np.uint8(0)).astype(np.uint8)
        pass
    else:
        new_red = np.where(redish(channel, channel2, channel3),
                           channel,
                           np.uint8(0)).astype(np.uint8)
        pass

    # The number of dimensions of the tiles (excluding the channel dimension)
    n = img.image.ndim - 1

    # Select the slice of the old_tiles array to replace
    replace_slice = [slice(None)] * n + [img.colors[mainchannel]]

    # Use advanced indexing and slicing to assign the new tiles to the old tiles
    img.image[replace_slice] = new_red

    return img
