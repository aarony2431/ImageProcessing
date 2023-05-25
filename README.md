# ImageProcessing

`ImageProcessing` is a Python library designed to automate batch-scale processing and analysis of large TIFF images. The `ImageProcessing` methods are designed for use with immunofluorescence images on black backgrounds or punctate dots on white background, histology images, especially [RNAscope](https://acdbio.com/rnascope%E2%84%A2-basescope%E2%84%A2-and-mirnascope%E2%84%A2assays). The `ImageProcessing` module contains loop- and multiprocessing-based methods to automate any method used to process images, and contains methods to process images for RNAscope and colocalization using several well known methods such as [Costes](https://imagej.net/media/costes-etalcoloc.pdf), [Pearson's and Mander's Correlation Coefficients](https://imagej.net/media/manders.pdf), and [median subtraction](https://en.wikipedia.org/wiki/Median_filter).

Recently, `ImageProcessing` has been upgraded to include some Python functionalities of standard [ImageJ](https://imagej.net) functions to circumvent memory limitations of [PyImageJ](https://github.com/imagej/pyimagej). This includes other image manipulation helper functions.

## Installation

TBD

## Usage

Several helper functions are provided in the base package. These include
- `ImageTiff` - a wrapper class for `PIL.Image` and `numpy.ndarray` that allows for streamlined functionality of TIFF images
- `copy` - a system function used to identically copy the bytes of one file to another location
- `decompress` - a system function used to naturally decompress any image
- `subtractmedian` - an image processing function which subtracts the local median intensity from each pixel
- `processimage` - a single wrapper function for processing and then saving an image using several different image handling libraries
- `processimage_pool` and `processimage_loop` - batch functions to use with `processimage`

Batch image processing can be performed by importing the `processimage` module and applying it to some image processing function. This function may be a supplied function or a user-defined function. Use the `**kwargs` argument to pass values to any supplied or user-defined function.
```
from ImageProcessing.src import processimage, processimage_loop, processimage_pool
from ImageProcessing.src.RNAscope import thresholdchannel

func = thresholdchannel

processimage(func, imagepath, **kwargs)
processimage_loop(func, imagepaths, logdir=log_file_directory, **kwargs)
processimage_pool(func, imagepaths, logdir=log_file_directory, **kwargs)
```

### ImageJ

Python ports of classic ImageJ functions. Currently contains the following (in no particular order):
- basic unit conversions using image metadata
- Find Maxima
- Threshold (Huang)
- Analyze Particles
- Options

### RNAscope

Relative RNAscope counts can be obtained using the `getcounts()` function utilizing either OpenCV or PyImageJ. 
```
from ImageProcessing.src.RNAscope import getcounts

getcounts(inputDir, outputDir, algorithm='opencv', **kwargs)
getcounts(inputDir, outputDir, algorithm='imagej', **kwargs)
```

A detailed description of the valid `**kwargs` is below.

**OpenCV and Python**
- if the user supplies the keyword argument `func`, all other `kwargs` will be passed to `func` and all images will be processed only with `func` and using `kwargs`
- To be supplied to `_batch_getcounts_opencv` and `_getcounts_opencv`
  -  `save_threshold_image_dir`: a boolean indicating if the thresholded images are to be saved
- To be supplied to `threshold_huang()`:
  - `threshold_channel`: the channel number or color to be used for thresholding
  - `tile_size`: a tuple specifying the size of the tile to be used if tiling of the image is desired
  - `white_background`: a boolean indicating if the image has a light background (bright field) or dark background (fluorescence)
- To be supplied to `ParticleAnalyzer()`:
  - `area`: a tuple indicating the min and max areas of identified objects
  - `threshold`: a tuple indicating the min and max thresholds to use
  - `threshold_step`: the threshold step
  - `circularity`: a tuple of floats between 0 and 1 indicating the min and max circularity
  - `convexity`: a tuple of floats between 0 and 1 indicating the min and max convexity
  - `inertia_ratio`: a tuple of floats between 0 and 1 indicating the min and max inertia ratio
- To be supplied to `ParticleAnalyzer.options()`:
  - `options_size`: the size of the kernel to be used for morphology options
  - `iterations`: the number of iterations that each option will be done
- To be supplied to `FindMaxima()`:
  - `maxima_channel`: the channel number or color to be used for maxima identification
  - `tile_size`: a tuple specifying the size of the tile to be used if tiling of the image is desired
  - `noise_tolerance`: the cutoff for noise, equivalent to ImageJ's `prominence`
  - `neighborhood_size`: the size of the neighborhood that is used to determine maxima
- To be supplied to unit conversions:
  - `xResolution_tag`: the tag name or number for the X Resolution in metadata (default 282)
  - `yResolution_tag`: the tag name or number for the Y Resolution in metadata (default 283)
  - `ResolutionUnit_tag`: the tag name or number for the Resolution Units in metadata (default 296)
  - `collapse_resolutions`: a boolean indicating whether or not to average the Resolution Units in the X and Y directions or keep them separated



**PyImageJ**
- `fiji_version`: a string representing the version of fiji to use (default is the computer's `'native'`)
- `macro`: the ImageJ macro to be performed, written in the ImageJ Macro language (default macro is already supplied)

For RNAscope using PyImagej, please first ensure that the [PyImageJ module](https://github.com/imagej/pyimagej) is installed and activated by using
```
conda install mamba -n base -c conda-forge
mamba create -n pyimagej -c conda-forge pyimagej openjdk=8
conda activate pyimagej
```
or
```
pip install pyimagej
```

### Colocalization

TBD

### Examples

**Batch processing images for H&E RNAscope processing and analysis:**
```
from ImageProcessing.src import processimage_pool
from ImageProcessing.src.RNAscope import thresholdchannel

inputDir = ...
outputDir = ...
imagepaths = [image
              for root, dirs, files in os.walk(inputDir)
              for image in glob(join(root, '*.[Tt][Ii][Ff]'))
              if not islink(image)]

# The kwargs to supplied to the function, thresholdchannel
kwargs = {
  'mainchannel': 'red',
  'C2channel': 'green',
  'C3channel': 'blue',
  'whitebackground': True,
  'loop': False
}

# Set the maximum number of processes to avoid overclocking
processes = len(psutil.Process().cpu_affinity()) - 1

processimages_pool(thresholdchannel,
                   imagepaths,
                   processes=processes,
                   chunksize=10,
                   logdir=outputDir,
                   out=outputDir,
                   isbgr=False,
                   heirarchy_inputDir=inputDir,
                   tilesize=1024,
                   image_library='memmap_fast',
                   **kwargs)
```

Every image in the directory and subdirectories of `inputDir` is analyzed and the processed images and log files are outputted into `outputDir`, maintaing the hierarchy of the original directory. The image is assumed to be an RGB image, where the channel of interest is _red_, the secondary channel is _green_, and the tertiary channel is _blue_, and the image is a brightfield image with a light background. The images will be processed in tiles of size 1024x1024 using a fast version of `np.memmap`.

```
from ImageProcessing.src.RNAscope import getcounts

inputDir = processedimageDir
outputDir = resultsDir

kwargs = {
  # OpenCV kwargs
  'save_threshold_image_dir' = True,
  
  # Huang thresholding kwargs
  'threshold_channel' = 'blue',  # required kwarg!!!
  # 'tile_size' = 1024,
  'white_background' = True,
  
  # ParticleAnalyzer kwargs
  # 'area': (10, 1000000),
  # 'threshold': (0, 255),
  # 'circularity': (0.1, 1.0),
  # 'convexity': (0.87, 1.0),
  # 'inertia_ratio': (0.1, 1.0),
  
  # FindMaxima kwargs
  'maxima_channel' = 'red',   # required kwarg!!!
  'tile_size' = (16384, 16384),
  'noise_tolerance' = 1.0,
  'neighborhood_size' = 3,
  
  # Unit conversion kwargs
  # 'xResolution_tag' = 282,
  # 'yResolution_tag' = 283,
  # 'ResolutionUnit_tag' = 296,
  # 'collapse_resolutions' = True,
  
  # Binary Options kwargs
  # 'options_size' = 1,
  'iterations' = 3
}
getcounts(inputDir, outputDir, algorithm='opencv', **kwargs)
```

Each of the processed images from the previous output is processed in batch. The images will each be thresholded using Huang's thresholding method on the _blue_ channel, without tiling and assuming the the image is a light background image. The ParticleAnalyzer and UnitConverters are used with default parameters. BinaryOptions are iterated 3 times on the Huang-thresholded images to generate the resulting images which will be saved in `outputDir` based on the `save_threshold_image_dir` flag and used to calculate the total sample area. Local image maxima are identified on the _red_ channel with a base value of at least 1.0 using the neighbors in a 3x3 centered square, using a tiled approach of 16384x16384 tiles. Local image measurements are outputted as _imagename, imagepath, number of maxima, tissue area, image area, dots per unit area, tissue to image ratio_ as a `.csv` file in `outputDir`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
