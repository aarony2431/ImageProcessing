from os.path import dirname, join, getsize
from os import remove

from ..src import decompress, copy


def test_decompress():
    test_image = r"SP-012102_1001.22 adrenal gland_Mfa-SSB-O1_Default_Extendedlf.tif"

    # folder_path = dirname(inspect.getfile(test_maxima))
    folder_path = r"F:\Aaron Y - extra space\Orbit H&E\Cyno TIF annotations - output\too big\input compressed"
    image_path = join(folder_path, test_image)

    # Decompression tests
    copy_file = copy(image_path, folder_path)
    assert 205691454 == getsize(copy_file)
    remove(copy_file)
    decompress_file = decompress(image_path, folder_path)
    assert 670433680 == getsize(decompress_file)
    remove(decompress_file)
    pass
