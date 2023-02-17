import csv
import os.path
from glob import glob

import imagej
import scyjava
import time

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

results = filename + "\t" + count + "\t" + area + "\t" + dot_area_ratio + "\t" + area_ratio;
"""


# def processimage(image_path: str):
#     start_time = time.perf_counter()
#     [n, total, imagepath] = image_path.split('\t')
#     print(f'Now processing {n}/{total}: {os.path.basename(imagepath)}')
#     ij = imagej.init(r'E:\Aaron Y\Fiji.app', mode='interactive')
#     # ij = imagej.init('sc.fiji:fiji:2.5.0')
#     args = {'imagepath': os.path.abspath(imagepath)}
#     result = ij.py.run_macro(macro, args)
#     print(
#         f'{n}/{total}: {os.path.basename(imagepath)} was processed in {time.perf_counter() - start_time: .2f} seconds...')
#     return str(result.getOutput('results')).split('\t')
#
#
# def processimage_test(image_path: str):
#     start_time = time.perf_counter()
#     path = r"E:\Aaron Y\Data\Orbit H&E\OG tiff files annotations - output\1003_Lung_Threshold_red.tif"
#     [n, total, imagepath] = image_path.split('\t')
#     print(f'Now processing {n}/{total}: {os.path.basename(imagepath)}')
#     ij = imagej.init(r'E:\Aaron Y\Fiji.app', mode='interactive')
#     # ij = imagej.init('sc.fiji:fiji:2.5.0')
#     args = {'imagepath': os.path.abspath(path)}
#     result = ij.py.run_macro(macro, args)
#     print(
#         f'{n}/{total}: {os.path.basename(imagepath)} was processed in {time.perf_counter() - start_time: .2f} seconds...')
#     return str(result.getOutput('results')).split('\t')


def getcounts(inputdir: str, outputdir: str, fiji_version='native'):
    inputDir = os.path.abspath(inputdir)
    outputDir = os.path.abspath(outputdir)

    imagepaths = [y for x in os.walk(inputDir) for y in glob(os.path.join(x[0], '*.[Tt][Ii][Ff]'))]

    start = time.perf_counter()

    # results = processimage_test('1\t1\tC://')

    # # pool = Pool(processes=max(len(psutil.Process().cpu_affinity()) - 1, 1))
    # pool = Pool(processes=4)
    # results = pool.imap(processimage,
    #                     [f'{i+1}\t{len(imagepaths)}\t{imagepath}' for i, imagepath in enumerate(imagepaths)])
    # # results = pool.imap(processimage_test, [f'{i}\t{len(imagepaths)}\t{imagepath}' for i, imagepath in enumerate(imagepaths)])
    # pool.close()
    # pool.join()

    results = []
    fiji = r'E:\Aaron Y\Fiji.app' if fiji_version == 'native' else f'sc.fiji:fiji:{fiji_version}'
    ij = imagej.init(fiji, mode='interactive')
    # ij = imagej.init('sc.fiji:fiji:2.5.0', mode='interactive')
    for n, imagepath in enumerate(imagepaths):
        total = len(imagepaths)
        print(f'Now processing {n+1}/{total}: {os.path.basename(imagepath)}')

        start_time = time.perf_counter()
        args = {'imagepath': os.path.abspath(imagepath)}
        result = ij.py.run_macro(macro, args)
        results.append(str(result.getOutput('results')).split('\t'))
        print(
            f'{n+1}/{total}: {os.path.basename(imagepath)} was processed in {time.perf_counter() - start_time: .2f} seconds...')
        pass

    with open(os.path.join(outputDir, 'DotCounts.csv'), 'w', encoding='utf-8', newline='\n') as f:
        writer = csv.writer(f, delimiter='\t')
        header = ['Image Name',
                  'Dot Maxima',
                  'Area (um^2)',
                  'Dots per um^2',
                  'Identified area to image size ratio (for QC)'
                  ]
        writer.writerow(header)
        writer.writerows(results)
        f.close()
        pass

    print(f'Processes finished in {time.perf_counter() - start: .2f} seconds.')
    pass

