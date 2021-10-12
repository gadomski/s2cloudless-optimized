from typing import Dict, Any

import rasterio
import numpy

import scipy.ndimage.filters
import skimage.morphology


def cloud_mask(
    probabilities: numpy.ndarray,
    threshold: float = 0.4,
    average_over: float = 1.0,
    dialation_size: float = 1.0,
) -> numpy.ndarray:
    """Calculates a cloud mask from the given probabilities."""
    convolution_filter = skimage.morphology.disk(average_over) / numpy.sum(
        skimage.morphology.disk(average_over)
    )
    cloud_mask = (
        scipy.ndimage.filters.convolve(probabilities, convolution_filter) > threshold
    ).astype(numpy.int8)
    dilation_filter = skimage.morphology.disk(dialation_size)
    cloud_mask = skimage.morphology.dilation(cloud_mask, dilation_filter).astype(
        numpy.int8
    )
    return cloud_mask


def write(path: str, data: numpy.ndarray, profile: Dict[str, Any]):
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(data, 1)
