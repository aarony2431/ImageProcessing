import csv
import logging
import os.path
from contextlib import redirect_stdout, redirect_stderr
from glob import glob
from typing import Literal, Any, Callable

import imagej
import numpy as np
import scyjava
import time

from tqdm import tqdm
from PIL import Image

from ..ImageJ import FindMaxima, ParticleAnalyzer, threshold_huang, image_size_microns, \
    convert_pixel_to_area, options

# this code runs using the basic pyimagej environment created using
#   conda install mamba -n base -c conda-forge
#   mamba create -n pyimagej -c conda-forge pyimagej openjdk=8
#   conda activate pyimagej

scyjava.config.add_option('-Xmx24g')
# scyjava.config.add_option(r'-Dplugins.dir=E:\Aaron Y\Fiji.app\plugins')

default_macro = """
#@ String imagepath
#@output String results

filename = File.getName(imagepath);
filedir = File.getDirectory(imagepath);

args = "open=[" + imagepath + "] autoscale color_mode=Default view=Hyperstack stack_order=XYCZT";
run("Bio-Formats Importer", args);
run("Stack to RGB");
close(filename);
selectWindow(filename + " (RGB)");
rename(filename);

run("Split Channels");
dot_image = filename + " (red)";
area_image = filename + " (blue)";
other_image = filename + " (green)";
close(other_image);

selectWindow(dot_image);
run("Find Maxima...", "prominence=0 output=Count");
count = getResult("Count");
close(dot_image);
close("Results");

selectWindow(area_image);
setAutoThreshold("Huang");
run("Convert to Mask");
run("Options...", "iterations=2 count=1 black do=Dilate");
run("Options...", "iterations=3 count=1 black do=Close");
run("Fill Holes");
run("Analyze Particles...", "display clear add");
// areas = Table.getColumn("Area");
total_area = 0;
for(i = 0; i < nResults; i++){
    total_area = total_area + getResult("Area", i);
}
if (total_area == 0) {
    total_area = getResult("Area", 0);
}
// ranked = Array.rankPositions(areas);
// area = ranked[Table.size - 1];
roiManager("Deselect");
roiManager("Delete");
close("ROI Manager")
getStatistics(area, mean, min, max, std, histogram)
close(area_image);
close("Results");

dot_area_ratio = 1.0 * count / total_area;
area_ratio = 1.0 * total_area / area;

results = filename + "\t" + filedir + "\t" + count + "\t" + total_area "\t" + area + "\t" + dot_area_ratio + "\t" + area_ratio;
"""

default_header = ['Image Name',
                  'Directory Path',
                  'Dot Maxima',
                  'Tissue Area (um^2)',
                  'Total Image Area (um^2)',
                  'Dots per um^2',
                  'Identified area to image size ratio (for QC)'
                  ]


def getcounts(inputdir: str | os.PathLike,
              outputdir: str | os.PathLike,
              /,
              *,
              algorithm: Literal['opencv', 'imagej'] = 'opencv',
              header: list = None,
              **kwargs):
    if algorithm == 'opencv':
        opencv_keys = ['save_threshold_image_dir', 'func']
        opencv_kwargs = {k: kwargs.pop(k) for k in opencv_keys if k in kwargs}
        results = _batch_getcounts_opencv(inputdir, **opencv_kwargs, **kwargs)
        pass
    elif algorithm == 'imagej':
        imagej_keys = ['fiji_version', 'macro']
        imagej_kwargs = {k: v for k, v in kwargs.items() if k in imagej_keys}
        results = _batch_getcounts_imagej(inputdir, **imagej_kwargs)
        pass
    else:
        raise ValueError(f'Invalid value for *algorithm*!')
    if not header:
        header = default_header
    _write(results, outputdir, header=header)
    pass


def _getcounts_imagej(imagepath: str | os.PathLike,
                      /,
                      *,
                      imagej_object: Any | None = None,
                      fiji_version: str | None = None,
                      macro: str = None) -> list:
    if not imagej_object:
        if fiji_version:
            fiji = r'E:\Aaron Y\Fiji.app' if fiji_version == 'native' else f'sc.fiji:fiji:{fiji_version}'
            ij = imagej.init(fiji, mode='interactive')
        else:
            raise KeyError(f'A version for *fiji_version* must be specified if a PyImageJ handler is not supplied!')
    else:
        ij = imagej_object
        args = {'imagepath': os.path.abspath(imagepath)}
        try:
            logging.basicConfig(level=logging.ERROR)
            with redirect_stdout(os.devnull), redirect_stderr(os.devnull):
                if not macro:
                    macro = default_macro
                pyimagej_results = ij.py.run_macro(macro, args)
                result = str(pyimagej_results.getOutput('results')).split('\t')
        except Exception as e:
            print(e)
            result = None
    return list(result)


def _batch_getcounts_imagej(inputdir: str | os.PathLike,
                            /,
                            *,
                            fiji_version: str = 'native',
                            macro: str = default_macro) -> list:
    inputDir = os.path.abspath(inputdir)

    # Ensure input and output are properly defined
    if inputDir != '':
        imagepaths = [image
                      for root, dirs, files in os.walk(inputDir)
                      for image in glob(os.path.join(root, '*.[Tt][Ii][Ff]'))
                      if not os.path.islink(image)]
        if len(imagepaths) == 0:
            raise ValueError(f'*inputdir* is empty!')

        results = []
        fiji = r'E:\Aaron Y\Fiji.app' if fiji_version == 'native' else f'sc.fiji:fiji:{fiji_version}'
        ij = imagej.init(fiji, mode='interactive')
        # ij = imagej.init('sc.fiji:fiji:2.5.0', mode='interactive')
        for imagepath in tqdm(imagepaths):
            result = []
            try:
                logging.basicConfig(level=logging.ERROR)
                with redirect_stdout(os.devnull), redirect_stderr(os.devnull):
                    result = _getcounts_imagej(imagepath, imagej_object=ij, macro=macro)
            except Exception as e:
                print(e)
            finally:
                results.append(result)
    else:
        raise ValueError(f'*inputdir* is not properly defined!')
    return results


def _write(results: list | Any,
           outputdir: str | os.PathLike,
           /,
           *,
           header: list = None,
           delimiter: str = '\t'):
    with open(os.path.join(outputdir, f'Counts_{time.time_ns()}.csv'), 'w', encoding='utf-8', newline='\n') as f:
        writer = csv.writer(f, delimiter=delimiter)
        if not header:
            header = default_header
        writer.writerow(header)
        writer.writerows(results)
        f.close()
        pass
    pass


def _getcounts_opencv(imagepath: str | os.PathLike,
                      /,
                      *,
                      save_threshold_image_dir: str | os.PathLike | None = None,
                      func: Callable = None,
                      **kwargs) -> list:
    try:
        if func:
            result = func(imagepath, **kwargs)
            pass
        else:
            threshold_keys = ['threshold_channel', 'tile_size', 'white_background']
            threshold_kwargs = {k: v for k, v in kwargs.items() if k in threshold_keys}
            if 'threshold_channel' not in threshold_kwargs.keys():
                raise KeyError(f'Must specify a channel to be thresholded for the area!')
            particleanalyzer_keys = ['area', 'threshold', 'threshold_step', 'circularity', 'convexity', 'inertia_ratio']
            particleanalyzer_kwargs = {k: v for k, v in kwargs.items() if k in particleanalyzer_keys}
            findmaxima_keys = ['maxima_channel', 'tile_size', 'noise_tolerance', 'neighborhood_size']
            findmaxima_kwargs = {k: v for k, v in kwargs.items() if k in particleanalyzer_kwargs}
            if 'maxima_channel' not in findmaxima_kwargs.keys():
                raise KeyError(f'Must specify a channel for maxima identification!')
            units_keys = ['xResolution_tag', 'yResolution_tag', 'ResolutionUnit_tag', 'collapse_resolutions']
            units_kwargs = {k: v for k, v in kwargs.items() if k in units_keys}
            options_keys = ['options_size', 'iterations']
            options_kwargs = {k: v for k, v in kwargs.items() if k in options_keys}

            # Threshold the image on the selected channel
            threshold_array = threshold_huang(imagepath, **threshold_kwargs)
            # Use Particle Analyzer to get standard tissue outlines
            analyzer = ParticleAnalyzer(**particleanalyzer_kwargs)
            # Dilate and close to connect any difficult areas and ensure the tissue it enclosing itself
            threshold_array = options(threshold_array, option='dilate', **options_kwargs)  # Dilate
            threshold_array = options(threshold_array, option='dilate', **options_kwargs)  # Close
            if save_threshold_image_dir:
                filename = os.path.basename(imagepath)
                filebase, ext = os.path.splitext(filename)
                newfilepath = os.path.join(save_threshold_image_dir, f'{filebase}_THRESHOLD{ext}')
                Image.fromarray(threshold_array).save(newfilepath)
                pass
            # Use Particle Analyzer to get the tissues in new threshold matrix
            # might not have to. might not be able to get area using cv2.KeyPoints
            # instead try just counting nonzero pixels?
            # particles = analyzer.detect(threshold_array)
            # Get tissue area
            tissue_pixels = np.count_nonzero(threshold_array)
            tissue_area = convert_pixel_to_area(tissue_pixels, image=imagepath, **units_kwargs)
            # Get image area
            image_height, image_width = image_size_microns(imagepath, **units_kwargs)
            # Get dot counts
            num_maxima = FindMaxima(imagepath, **findmaxima_kwargs)

            result = []
            result[0] = os.path.basename(imagepath)  # Image name
            result[1] = os.path.dirname(imagepath)  # Image path
            result[2] = num_maxima  # Dot Count
            result[3] = tissue_area  # Tissue area
            result[4] = image_height * image_width  # Image Area
            result[5] = result[2] / result[3]  # Dots per unit area
            result[6] = result[3] / result[4]  # Tissue to image area ratio (for QC)
            pass
        pass
    except Exception as e:
        print(e)
        result = None
    return list(result)


def _batch_getcounts_opencv(inputdir: str | os.PathLike, save_threshold_image_dir: str | os.PathLike | None = None,
                            func: Callable | None = None, **kwargs) -> list:
    inputDir = os.path.abspath(inputdir)

    # Ensure input and output are properly defined
    if inputDir != '':
        imagepaths = [image
                      for root, dirs, files in os.walk(inputDir)
                      for image in glob(os.path.join(root, '*.[Tt][Ii][Ff]'))
                      if not os.path.islink(image)]
        if len(imagepaths) == 0:
            raise ValueError(f'*inputdir* is empty!')
        results = []
        for imagepath in tqdm(imagepaths):
            result = []
            try:
                result = _getcounts_opencv(imagepath, save_threshold_image_dir=save_threshold_image_dir, **kwargs)
            except Exception as e:
                print(e)
            finally:
                results.append(result)
    else:
        raise ValueError(f'*inputdir* is not properly defined!')
    return results
