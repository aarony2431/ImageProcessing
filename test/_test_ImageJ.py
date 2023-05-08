import inspect

from os.path import dirname, join, splitext

import numpy as np
from PIL import Image
from ..src.ImageJ import threshold_huang, ParticleAnalyzer, FindMaxima, convert_pixel_to_area, image_size_microns, pixels_per_micron


def test_imagej():
    _test_threshold()
    _test_maxima()
    pass


def _test_maxima():
    test_image = r"SP-012102_1001.22 adrenal gland_Mfa-SSB-O1_Default_Extendedlf_Processed.tif"

    # folder_path = dirname(inspect.getfile(test_maxima))
    folder_path = r"F:\Aaron Y - extra space\Orbit H&E\Cyno TIF annotations - output" \
                  r"\too big\2nd output processed image for reference"
    image_path = join(folder_path, test_image)

    # Threshold the blue channel to get image area
    # thresholded_image_array = threshold_huang(image_path, color_channel='blue')
    # Generate particle analyzer
    # particle_analyzer = ParticleAnalyzer()
    # Apply particle analyzer to thresholded image
    # Dilate and close holes, then sum particles together to get total area

    # Find Maxima tests
    chunk_size = int(2 ** 14)
    assert 639082 == FindMaxima(image_path, maxima_channel='red', noise_tolerance=1.0)
    assert 639116 == FindMaxima(image_path, maxima_channel='red', noise_tolerance=1.0,
                                tile_size=(chunk_size, chunk_size))
    pass


def _test_threshold():
    test_image = r"SP-012102_1001.22 adrenal gland_Mfa-SSB-O1_Default_Extendedlf_UNCOMPRESSED.tif"

    # folder_path = dirname(inspect.getfile(test_maxima))
    folder_path = r"F:\Aaron Y - extra space\Orbit H&E\Cyno TIF annotations - output\too big\uncompressed"
    image_path = join(folder_path, test_image)

    # Threshold test
    thresholded_image_array = threshold_huang(image_path, threshold_channel='blue')
    assert 92304771 == np.count_nonzero(thresholded_image_array)
    assert np.round(5732015.582172504) == np.round(convert_pixel_to_area(np.count_nonzero(thresholded_image_array),
                                                                         image=image_path))
    # currently not working in chunks
    # chunk_size = int(2 ** 12)
    # thresholded_image_array = threshold_huang(image_path, color_channel='blue', tile_size=(chunk_size, chunk_size))
    # filebase, ext = splitext(test_image)
    # threshold_image = join(folder_path, f'{filebase}_THRESHOLD{ext}')
    # Image.fromarray(thresholded_image_array).save(threshold_image)
    # print(np.count_nonzero(thresholded_image_array))
    pass
