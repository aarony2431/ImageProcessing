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
        cutoff = 85

        # Filter out elements that don't satisfy red > cutoff
        # Improve downstream processing time
        mask = r > cutoff
        r = r[mask]
        g = g[mask]
        b = b[mask]

        def isnotred_greencorrection(red, green, blue):
            c1factor = 1
            c2factor = 1.15
            condition2 = green > cutoff
            condition3 = blue > cutoff
            condition4 = red > green * c1factor
            condition5 = green > blue * c2factor
            return np.logical_and.reduce([condition2, condition3, condition4, condition5])

        def isred_bluecorrection(red, green, blue):
            green_factor = 1.1
            red_blue_offset_ratio = 0.15
            red_blue_max = np.maximum(red, blue)
            condition2 = red > green * green_factor
            condition3 = red > blue * green_factor
            condition4 = 1 - (red / red_blue_max) <= red_blue_offset_ratio
            condition5 = 1 - (blue / red_blue_max) <= red_blue_offset_ratio
            return np.logical_and.reduce([condition2, condition3, condition4, condition5])

        def isred(red, green, blue):
            factor1 = 1.3
            factor2 = 1.15
            mean_offset_ratio = 0.15

            # Calculate mean and differences from mean
            mean = np.mean(np.stack((green, blue), axis=-1), axis=-1)
            green_diff = np.abs(green - mean)
            blue_diff = np.abs(blue - mean)

            red_green_condition = red > green * factor1 and red > blue * factor1
            red_offset_condition = green_diff < mean * mean_offset_ratio and blue_diff < mean * mean_offset_ratio and red > green * factor2 and red > blue * factor2
            return np.logical_or(red_green_condition, red_offset_condition)

        # Logical processing to determine if color is red
        if not isnotred_greencorrection(r, g, b) and (isred(r, g, b) or isred_bluecorrection(r, g, b)):
            return True
        else:
            return False

    channel = img.colors[mainchannel]
    channel2 = img.colors[C2channel]
    channel3 = img.colors[C3channel]
    img.image[:, : channel] = np.where(redish(img.image[:, : channel],
                                              img.image[:, : channel2],
                                              img.image[:, : channel3]),
                                       np.uint8(255) - img.image[:, : channel] if
                                        whitebackground else img.image[:, : channel], np.uint8(0))

    return img

