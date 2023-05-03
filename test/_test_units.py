import numpy as np

from os.path import join
from ..src.ImageJ import pixels_per_micron, image_size_microns


def test_units():
    test_image = r"SP-012102_1001.22 adrenal gland_Mfa-SSB-O1_Default_Extendedlf_UNCOMPRESSED.tif"

    # folder_path = dirname(inspect.getfile(test_maxima))
    folder_path = r"F:\Aaron Y - extra space\Orbit H&E\Cyno TIF annotations - output\too big\uncompressed"
    image_path = join(folder_path, test_image)

    assert np.round(100 * 4.012900517616721) == np.round(100 * pixels_per_micron(image_path))
    assert np.round(100 * (7017.368079865669, 1977.6219134166886)) == np.round(100 * image_size_microns(image_path))
