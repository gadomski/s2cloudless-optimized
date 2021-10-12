# s2cloudless-optimized

A derivative work of https://github.com/sentinel-hub/sentinel2-cloud-detector/, optimized for lower memory footprint.
We re-use the LightGBM model from sentinel2-cloud-detector, but optimize the reading of source data files and numpy array manipulation to keep the memory footprint as low as possible.


## Installation

```shell
$ pip install git+https://github.com/gadomski/s2cloudless-optimized
```

### macOS

On macOS, the upstream library LightGBM is [incompatible with the Homebrew-provided libomp](https://github.com/microsoft/LightGBM/issues/4229).
This means you will need to use conda to install OpenMP before installing the Python package:

```shell
$ conda install --name s2cloudless-optimized -c conda-forge -y llvm-openmp
$ conda activate s2cloudless-optimized
$ pip install git+https://github.com/gadomski/s2cloudless-optimized
```


## Usage

You'll need to have a locally-available Sentinel2 L1C granule.
L1C data often look something like this:

```shell
$ tree -d S2A_MSIL1C_20150726T105026_N0204_R051_T31TDH_20150726T105856.SAFE 
S2A_MSIL1C_20150726T105026_N0204_R051_T31TDH_20150726T105856.SAFE
├── DATASTRIP
│   └── DS_EPA__20160813T073138_S20150726T105856
├── GRANULE
│   └── L1C_T31TDH_A000477_20150726T105856
│       ├── IMG_DATA
│       └── QI_DATA
├── HTML
└── rep_info
```

The granule directory in this case would be `S2A_MSIL1C_20150726T105026_N0204_R051_T31TDH_20150726T105856.SAFE/GRANULE/L1C_T31TDH_A000477_20150726T105856`.

The default behavior of both the command line interface and the API is to create Cloud Optimized GeoTIFFs (COGs) inside the `IMG_DATA` directory of the granule.
These geotiffs will have the suffixes `_probabilities` and `_cloud_mask`.
The probabilities geotiff is a uint8 COG with values between 0 and 100, indicating the likelyhood of cloud cover in the given pixel as determined by s2cloudless (100 means high probability of cloud).
The cloud mask geotiff is a uint8 COG with values of 0 or 1, with 1 indicating the presence of a cloud.

Both the probabilities and cloud mask geotiffs have nodata values of 255, as determined by values of 0 (nodata) or 65536 (saturated) in any of the source bands.

### Command line


```shell
$ s2cloudless S2A_MSIL1C_20150726T105026_N0204_R051_T31TDH_20150726T105856.SAFE/GRANULE/L1C_T31TDH_A000477_20150726T105856
```

### API

```python
import s2cloudless_optimized
directory = "S2A_MSIL1C_20150726T105026_N0204_R051_T31TDH_20150726T105856.SAFE/GRANULE/L1C_T31TDH_A000477_20150726T105856"
output_paths = s2cloudless_optimized.run(directory)
```
## License

This work is available under the same license as sentinel-hub/sentinel2-cloud-detector, the [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0)
