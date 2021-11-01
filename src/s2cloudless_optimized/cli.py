import logging
from typing import Optional, Union

import click
import click_log

import s2cloudless_optimized

from .constants import DEFAULT_COMPRESSION, DEFAULT_RESOLUTION
from .enums import HighLow

logger = logging.getLogger("s2cloudless_optimized")
click_log.basic_config(logger)


@click.command()
@click_log.simple_verbosity_option(logger)
@click.argument("DIRECTORY")
@click.option("-c", "--compression", type=str, default=DEFAULT_COMPRESSION)
@click.option("-r", "--resolution", type=str, default=str(DEFAULT_RESOLUTION))
@click.option("-o", "--output-directory", type=str)
def main(
    directory: str,
    compression: str,
    resolution: str,
    output_directory: Optional[str] = None,
):
    """Runs s2cloudless-optimized on the files in a given directory.

    Drops the cloud and probability mask as COGs in the same directory.
    """
    try:
        resolution_resolved: Union[float, HighLow] = HighLow(resolution)
    except ValueError:
        resolution_resolved = float(resolution)
    s2cloudless_optimized.run(
        directory,
        compression=compression,
        resolution=resolution_resolved,
        output_directory=output_directory,
    )
