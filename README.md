# ImageProcessing

**ImageProcessing** is a Python library designed to automate batch-scale processing and analysis of large TIFF images. The **ImageProcessing** methods are designed for use with immunofluorescence images on black backgrounds, especially [RNAscope](https://acdbio.com/rnascope%E2%84%A2-basescope%E2%84%A2-and-mirnascope%E2%84%A2assays). The **ImageProcessing** module contains loop- and multiprocessing-based methods to automate any method used to process images, and contains methods to process images for RNAscope and colocalization using several well known methods such as [Costes](https://imagej.net/media/costes-etalcoloc.pdf), [Pearson's and Mander's Correlation Coefficients](https://imagej.net/media/manders.pdf), and [median subtraction](https://en.wikipedia.org/wiki/Median_filter).

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
- Analyze Particles (work in progress)

### RNAscope

For RNAscope, please first ensure that the [PyImageJ module](https://github.com/imagej/pyimagej) is installed and activated by using
```
conda install mamba -n base -c conda-forge
mamba create -n pyimagej -c conda-forge pyimagej openjdk=8
conda activate pyimagej
```
or
```
pip install pyimagej
```
Relative RNAscope counts can be obtained using `getcounts` function which utilizes PyImageJ. 
```
from ImageProcessing.src.RNAscope import getcounts

getcounts(inputDir, outputDir)
```

### Colocalization

TBD

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
