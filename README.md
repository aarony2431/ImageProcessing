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

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
