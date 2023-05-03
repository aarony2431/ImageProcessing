import inspect

from os.path import dirname, join
from ImageProcessing.src.ImageJ import threshold_huang, ParticleAnalyzer, FindMaxima


def test_imagej():
    test_maxima()
    pass


def test_maxima():
    # Test imagepath
    image_path = r"F:\Aaron Y - extra space\Orbit H&E\Cyno TIF annotations - output\too big\uncompressed" \
                 r"\SP-012102_1001.22 adrenal gland_Mfa-SSB-O1_Default_Extendedlf_UNCOMPRESSED.tif"
    test_image = r"SP-012102_1001.22 adrenal gland_Mfa-SSB-O1_Default_Extendedlf_Processed.tif"

    # folder_path = dirname(inspect.getfile(test_maxima))
    folder_path = r"F:\Aaron Y - extra space\Orbit H&E\Cyno TIF annotations - output\2nd output\Adrenal"
    image_path = join(folder_path, test_image)

    # Threshold the blue channel to get image area
    # thresholded_image_array = threshold_huang(image_path, color_channel='blue')
    # Generate particle analyzer
    # particle_analyzer = ParticleAnalyzer()
    # Apply particle analyzer to thresholded image
    # Dilate and close holes, then sum particles together to get total area

    # Find Maxima tests
    chunk_size = int(2 ** 14)
    assert 639082 == FindMaxima(image_path, color_channel='red', noise_tolerance=1.0)
    assert 639116 == FindMaxima(image_path, color_channel='red', noise_tolerance=1.0,
                                tile_size=(chunk_size, chunk_size))
    pass
