import csv
import logging
import os.path
from contextlib import redirect_stdout, redirect_stderr
from glob import glob

import imagej
import scyjava
import time

from tqdm import tqdm

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


def getcounts(inputdir: str | os.PathLike, outputdir: str | os.PathLike, algorithm: Literal['opencv' | 'imagej'] = 'opencv', header: list = default_header, **kwargs):
    if algorithm == 'opencv':
        pass
    elif algorithm == 'imagej':
        keys = kwargs.keys()
        new_kwargs = {}
        if 'fiji_version' in keys:
            new_kwargs['fiji_version'] = keys['fiji_version']
        if 'macro' in keys:
            new_kwargs['macro'] = keys['macro']
        results = _batch_getcounts_imagej(inputdir, **new_kwargs)
        pass
    else:
        raise ValueError(f'Invalid value for *algorithm*!')
    _write(results, outputdir, header=header)
    pass

def _getcounts_imagej(imagepath: str | os.PathLike, imagej_object: Any | None = None, fiji_version: str | None = None, macro: str = default_macro) -> list:
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
                result = ij.py.run_macro(default_macro, args)
        except Exception as e:
            print(e)
    return list(str(result.getOutput('results')).split('\t'))


def _batch_getcounts_imagej(inputdir: str | os.PathLike, fiji_version: str = 'native', macro: str = default_macro) -> list:
    inputDir = os.path.abspath(inputdir)
    
    # Ensure input and output are properly defined
    if inputDir != '':
        imagepaths = [image
                      for root, dirs, files in os.walk(inputDir)
                      for image in glob(os.path.join(root, '*.[Tt][Ii][Ff]'))
                      if not os.path.islink(image)]
        if len(imagepaths) == 0:
            raise ValueError(f'*inputdir* is not properly defined!')
        
        results = []
        fiji = r'E:\Aaron Y\Fiji.app' if fiji_version == 'native' else f'sc.fiji:fiji:{fiji_version}'
        ij = imagej.init(fiji, mode='interactive')
        # ij = imagej.init('sc.fiji:fiji:2.5.0', mode='interactive')
        for imagepath in tqdm(imagepaths):
            try:
                logging.basicConfig(level=logging.ERROR)
                with redirect_stdout(os.devnull), redirect_stderr(os.devnull):
                    result = _getcounts_imagej(imagepath, imagej_object=ij, macro=macro)
            except Exception as e:
                print(e)
                result = None
            finally:
                results.append(result)
    else:
        raise ValueError(f'*inputdir* is not properly defined!')
    return results


def _write(results: list | Any, outputdir: str | os.PathLike, header: list = default_header, delimiter: str = '\t'):
    with open(os.path.join(outputDir, f'Counts_{time.time_ns()}.csv'), 'w', encoding='utf-8', newline='\n') as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(header)
        writer.writerows(results)
        f.close()
        pass
    pass

