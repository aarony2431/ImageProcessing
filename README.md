# ImageProcessing

**ImageProcessing** is a Python library designed to automate batch-scale processing and analysis of large TIFF images. The **ImageProcessing** methods are designed for use with immunofluorescence images on black backgrounds, especially [RNAscope](https://acdbio.com/rnascope%E2%84%A2-basescope%E2%84%A2-and-mirnascope%E2%84%A2assays). The **ImageProcessing** module contains loop- and multiprocessing-based methods to automate any method used to process images, and contains methods to process images for RNAscope and colocalization using several well known methods such as Costes, PCC, and median subtraction.

## Installation

TBD

## Usage

Batch image processing can be performed by importing the 'processimage' module and applying it to some image processing function. This function may be a supplied function or a custom function
```
from ImageProcessing.src import processimage, processimage_loop, processimage_pool
from ImageProcessing.src.RNAscope import thresholdchannel

func = thresholdchannel

processimage(func, imagepath, **kwargs)
processimage_loop(func, imagepaths, logdir=log_file_directory, **kwargs)
processimage_pool(func, imagepaths, logdir=log_file_directory, **kwargs)
```

For RNAscope, relative counts can be obtained using the [PyImageJ module](https://github.com/imagej/pyimagej). 
```
from ImageProcessing.src.RNAscope import getcounts

getcounts(inputDir, outputDir)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
