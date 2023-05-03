import os

import numpy as np
import tifffile as tiff


def pixels_per_micron(image: os.PathLike | str,
                      xResolution_tag: int | str | None = 282,
                      yResolution_tag: int | str | None = 283,
                      ResolutionUnit_tag: int | str | None = 296,
                      collapse_resolutions: bool = True) -> tuple[float, float] | float:
    tags = tiff.TiffFile(image).pages[0].tags
    # Get Resolution Units
    units = tags[ResolutionUnit_tag].value
    xres = tags[yResolution_tag].value
    yres = tags[xResolution_tag].value

    # Check if the tags were found
    if xres is None or yres is None or units is None:
        raise KeyError("Could not find pixel size information in the TIFF image.")
    else:
        # Convert the pixel size to microns
        if units == tiff.tifffile.RESUNIT.INCH:  # Units are inches
            microns_per_unit = float(25400)  # microns per unit
        elif units == tiff.tifffile.RESUNIT.CENTIMETER:  # Units are centimeters
            microns_per_unit = float(10000)  # microns per unit
        else:  # Units are meters
            microns_per_unit = float(1000000)  # microns per unit
    if collapse_resolutions:
        res = (yres[0] + xres[0]) / (yres[1] + xres[1])
        return res / microns_per_unit
    else:
        return (yres[0] / yres[1]) / microns_per_unit, (xres[0] / xres[1]) / microns_per_unit


def image_size_microns(image: os.PathLike | str,
                       xResolution_tag: int | str | None = 282,
                       yResolution_tag: int | str | None = 283,
                       ResolutionUnit_tag: int | str | None = 296,
                       collapse_resolutions: bool = True) -> tuple[float, float]:
    ppm = pixels_per_micron(image, xResolution_tag=xResolution_tag,
                            yResolution_tag=yResolution_tag, ResolutionUnit_tag=ResolutionUnit_tag,
                            collapse_resolutions=collapse_resolutions)
    shape = tiff.TiffFile(image).pages[0].shape
    pixel_height, pixel_width = (shape[0], shape[1])
    y_ppm, x_ppm = (ppm, ppm) if collapse_resolutions else ppm
    return pixel_height / y_ppm, pixel_width / x_ppm


def convert_pixel_to_area(pixel_area: int,
                          image: os.PathLike | str | None = None,
                          xResolution_tag: int | str | None = 282,
                          yResolution_tag: int | str | None = 283,
                          ResolutionUnit_tag: int | str | None = 296,
                          ppm: tuple[float, float] | None = None,
                          collapse_resolutions: bool = True) -> float:
    if image:
        ppm = pixels_per_micron(image, xResolution_tag=xResolution_tag,
                                yResolution_tag=yResolution_tag, ResolutionUnit_tag=ResolutionUnit_tag,
                                collapse_resolutions=collapse_resolutions)
    elif not ppm:
        raise KeyError(f'Please supply either the path *image* or a value for *ppm*!')
    y_ppm, x_ppm = (ppm, ppm) if collapse_resolutions else ppm
    return pixel_area / (y_ppm * x_ppm)
