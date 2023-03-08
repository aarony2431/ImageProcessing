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

macro = """
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
setAutoThreshold("Default");
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


def getcounts(inputdir: str, outputdir: str, fiji_version='native'):
    inputDir = os.path.abspath(inputdir)
    outputDir = os.path.abspath(outputdir)

    # Ensure input and output are properly defined
    if inputDir != '' and outputDir != '':
        imagepaths = [image
                      for root, dirs, files in os.walk(inputDir)
                      for image in glob(os.path.join(root, '*.[Tt][Ii][Ff]'))
                      if not os.path.islink(image)]

        start = time.perf_counter()

        results = []
        fiji = r'E:\Aaron Y\Fiji.app' if fiji_version == 'native' else f'sc.fiji:fiji:{fiji_version}'
        ij = imagej.init(fiji, mode='interactive')
        # ij = imagej.init('sc.fiji:fiji:2.5.0', mode='interactive')
        for imagepath in tqdm(imagepaths):

            args = {'imagepath': os.path.abspath(imagepath)}
            try:
                logging.basicConfig(level=logging.ERROR)
                with redirect_stdout(os.devnull), redirect_stderr(os.devnull):
                    result = ij.py.run_macro(macro, args)
            except Exception as e:
                print(e)
            results.append(str(result.getOutput('results')).split('\t'))
            print(
                f'{os.path.basename(imagepath)} was processed')
            pass

        with open(os.path.join(outputDir, 'DotCounts.csv'), 'w', encoding='utf-8', newline='\n') as f:
            writer = csv.writer(f, delimiter='\t')
            header = ['Image Name',
                      'Directory Path',
                      'Dot Maxima',
                      'Tissue Area (um^2)',
                      'Total Image Area (um^2)',
                      'Dots per um^2',
                      'Identified area to image size ratio (for QC)'
                      ]
            writer.writerow(header)
            writer.writerows(results)
            f.close()
            pass

        print(f'Processes finished in {time.perf_counter() - start: .2f} seconds.')
        pass
    pass

