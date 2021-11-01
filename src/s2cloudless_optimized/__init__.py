from typing import Optional, Union

from .constants import DEFAULT_COMPRESSION, DEFAULT_RESOLUTION
from .enums import HighLow
from .granule import Granule, OutputPaths


def run(
    directory: str,
    directory_is_granule: bool = True,
    compression: str = DEFAULT_COMPRESSION,
    resolution: Union[float, HighLow] = DEFAULT_RESOLUTION,
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
    return granule.run(
        resolution, compression=compression, output_directory=output_directory
    )
