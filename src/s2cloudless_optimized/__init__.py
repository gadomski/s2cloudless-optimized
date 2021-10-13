from typing import Optional, Union

from .enums import HighLow
from .granule import Granule, OutputPaths


def run(
    directory: str,
    directory_is_granule: Optional[bool] = True,
    resolution: Optional[Union[float, HighLow]] = None,
    output_directory: Optional[str] = None,
) -> OutputPaths:
    """Runs s2cloudless-optimized on the Sentinel2 L1C files in the given directory.

    Drops the cloud mask and probability mask in the same directory.

    Returns the resultant paths.
    """
    if directory_is_granule:
        granule = Granule.from_granule_path(directory)
    else:
        granule = Granule(directory)
    return granule.run(resolution, output_directory=output_directory)
