import dataclasses
import os
import pkg_resources
from typing import Optional, Union, Dict, Tuple, Iterator, Any

from lightgbm import Booster
import rasterio
import numpy

from .enums import HighLow
from . import utils


BANDS = ["B01", "B02", "B04", "B05", "B08", "B8A", "B09", "B10", "B11", "B12"]
DEFAULT_RESOLUTION = HighLow.HIGH


@dataclasses.dataclass
class OutputPaths:
    probabilities: str
    cloud_mask: str


@dataclasses.dataclass
class Profile:
    profile: Dict[str, Any]
    shape: Tuple[int, int]


@dataclasses.dataclass
class Prediction:
    probabilities: numpy.ndarray
    mask: numpy.ndarray
    profile: Profile


class Granule:
    """A granule directory containing sentinel2 L1C data."""

    """A dictionary of band -> path"""
    paths: Dict[str, str]

    def __init__(self, directory: str):
        """Creates from a directory containing IMG_DATA"""
        img_directory = os.path.join(directory, "IMG_DATA")
        if not os.path.isdir(img_directory):
            raise ValueError(
                f"{directory} is not a sentinel2 granule, does not contain an 'IMG_DATA' directory"
            )
        self.paths = dict()
        bands = set()
        for file_name in os.listdir(img_directory):
            basename, ext = os.path.splitext(file_name)
            if ext != ".jp2":
                continue
            parts = basename.split("_")
            band = parts[-1]
            if band in BANDS:
                self.paths[band] = os.path.join(img_directory, file_name)
                bands.add(band)
        if len(self.paths) != len(BANDS):
            missing_bands = set(BANDS) - bands
            raise ValueError(
                f"Invalid granule directory, missing bands: {missing_bands}"
            )

    def run(
        self, resolution: Optional[Union[float, HighLow]], compression: str = "lzw"
    ) -> OutputPaths:
        """Runs s2cloudless at the given resolution."""
        prediction = self._predict(resolution)
        return self._write(prediction, compression)

    def load(self, resolution: Optional[Union[float, HighLow]]) -> numpy.ndarray:
        """Loads in all image data at the given resolution."""
        profile = self._profile(resolution)
        data_shape = (profile.shape[0], profile.shape[1], len(BANDS))
        data = numpy.empty(data_shape)
        for i, band_data in enumerate(self._iter_band_data(profile.shape)):
            data[:, :, i] = band_data
        return data

    def _iter_band_data(self, shape: Tuple[int, int]) -> Iterator[numpy.ndarray]:
        for band in BANDS:
            path = self.paths[band]
            with rasterio.open(path) as dataset:
                data = (
                    dataset.read(1, out_shape=shape).astype(numpy.float32) / 10000
                )  # quantization value
                yield data

    def _predict(self, resolution: Optional[Union[float, HighLow]]) -> Prediction:
        profile = self._profile(resolution)
        s2cloudless_shape = (profile.shape[0] * profile.shape[1], len(BANDS))
        data = numpy.empty(s2cloudless_shape)
        mask = numpy.full(profile.shape, False)
        for i, band_data in enumerate(self._iter_band_data(profile.shape)):
            mask |= (band_data == 0) | (
                band_data == 65535
            )  # 0 is nodata, 65536 is saturated
            data[:, i] = band_data.reshape(s2cloudless_shape[0])

        model_filename = pkg_resources.resource_filename(
            __name__, "pixel_s2_cloud_detector_lightGBM_v0.1.txt"
        )
        booster = Booster(model_file=model_filename)
        prediction = booster.predict(data)
        return Prediction(
            probabilities=prediction.reshape(profile.shape),
            mask=mask,
            profile=profile,
        )

    def _output_paths(self) -> OutputPaths:
        """Returns the outputs paths in the granule IMG_DATA directory."""
        img_path = self.paths[BANDS[0]]
        base = "_".join(img_path.split("_")[:-1])
        return OutputPaths(
            probabilities=f"{base}_probabilities.tif",
            cloud_mask=f"{base}_cloud_mask.tif",
        )

    def _profile(self, resolution: Optional[Union[float, HighLow]]) -> Profile:
        profiles = dict()
        for path in self.paths.values():
            with rasterio.open(path) as dataset:
                res = dataset.res
                if res[0] in profiles:
                    continue
                elif res[0] != res[1]:
                    raise ValueError(
                        f"IMG file {path} has invalid resolution {dataset.res}, we expect both values to be equal"
                    )
                else:
                    profiles[res[0]] = dataset.profile

        if resolution is None:
            resolution = DEFAULT_RESOLUTION
        if isinstance(resolution, float):
            found_resolution = next((r for r in profiles if r == resolution), None)
            if not found_resolution:
                raise ValueError(
                    f"Requested resolution '{resolution}' is not a native resolution (native resolutions: {profiles.keys()})"
                )
            else:
                profile = profiles[found_resolution]
        elif resolution == HighLow.LOW:
            min_resolution = max(profiles.keys())
            profile = profiles[min_resolution]
        elif resolution == HighLow.HIGH:
            max_resolution = min(profiles.keys())
            profile = profiles[max_resolution]
        else:
            raise ValueError(f"Invalid resolution specifier: {resolution}")
        return Profile(profile=profile, shape=(profile["height"], profile["width"]))

    def _write(self, prediction: Prediction, compression: str) -> OutputPaths:
        cloud_mask = utils.cloud_mask(prediction.probabilities)
        cloud_mask[prediction.mask] = 255
        probabilities = numpy.clip(prediction.probabilities * 100, 0, 100).astype(
            numpy.uint8
        )
        probabilities[prediction.mask] = 255
        output_paths = self._output_paths()
        profile = prediction.profile.profile.copy()
        profile["driver"] = "COG"
        profile["nodata"] = 255
        profile["dtype"] = "uint8"
        profile["compression"] = compression
        utils.write(output_paths.probabilities, probabilities, profile)
        utils.write(output_paths.cloud_mask, cloud_mask, profile)
        return output_paths
