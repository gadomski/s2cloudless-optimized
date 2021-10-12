from tempfile import TemporaryDirectory

import rasterio

import s2cloudless_optimized


def test_run(granule_directory):
    with TemporaryDirectory() as temporary_directory:
        output_paths = s2cloudless_optimized.run(
            granule_directory, output_directory=temporary_directory
        )
        for path in [output_paths.probabilities, output_paths.cloud_mask]:
            with rasterio.open(path) as dataset:
                assert dataset.profile["dtype"] == "uint8"
                assert dataset.profile["driver"] == "GTiff"
