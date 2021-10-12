from typing import Optional, Union

from .granule import Granule, OutputPaths
from .enums import HighLow


def run(
    directory: str, resolution: Optional[Union[float, HighLow]] = None
) -> OutputPaths:
    """Runs s2cloudless-optimized on the Sentinel2 L1C files in the given directory.

    Drops the cloud mask and probability mask in the same directory.

    Returns the resultant paths.
    """
    granule = Granule(directory)
    return granule.run(resolution)
