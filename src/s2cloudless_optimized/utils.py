import logging
from typing import Any, Dict

import numpy
import rasterio
import scipy.ndimage.filters
import skimage.morphology

logger = logging.getLogger(__name__)

KEYS_TO_REMOVE = {"blockxsize", "blockysize", "tiled"}


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
    for key in KEYS_TO_REMOVE:
        if key in profile:
            del profile[key]
    logger.info(f"Writing {path} with profile: {profile}")
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(data, 1)
