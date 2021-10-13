import os.path
from tempfile import TemporaryDirectory

import rasterio

import s2cloudless_optimized
from s2cloudless_optimized.granule import OutputPaths


def assert_output_paths_ok(output_paths: OutputPaths):
    for path in [output_paths.probabilities, output_paths.cloud_mask]:
        with rasterio.open(path) as dataset:
            assert dataset.profile["dtype"] == "uint8"
            assert dataset.profile["driver"] == "GTiff"


def test_run(granule_directory):
    with TemporaryDirectory() as temporary_directory:
        output_paths = s2cloudless_optimized.run(
            granule_directory, output_directory=temporary_directory
        )
        assert_output_paths_ok(output_paths)


def test_run_with_exact_directory(granule_directory):
    img_data_directory = os.path.join(granule_directory, "IMG_DATA")
    with TemporaryDirectory() as temporary_directory:
        output_paths = s2cloudless_optimized.run(
            img_data_directory,
            directory_is_granule=False,
            output_directory=temporary_directory,
        )
        assert_output_paths_ok(output_paths)
