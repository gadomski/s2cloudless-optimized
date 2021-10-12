import logging
from typing import Optional, Union

import click
import click_log

import s2cloudless_optimized
from s2cloudless_optimized import HighLow

logger = logging.getLogger("s2cloudless_optimized")
click_log.basic_config(logger)


@click.command()
@click_log.simple_verbosity_option(logger)
@click.argument("DIRECTORY")
@click.option("-r", "--resolution", type=str)
@click.option("-o", "--output-directory", type=str)
def main(
    directory: str,
    resolution: Optional[str] = None,
    output_directory: Optional[str] = None,
):
    """Runs s2cloudless-optimized on the files in a given directory.

    Drops the cloud and probability mask as COGs in the same directory.
    """
    if resolution:
        try:
            resolution_resolved: Optional[Union[float, HighLow]] = HighLow(resolution)
        except ValueError:
            resolution_resolved = float(resolution)
    else:
        resolution_resolved = None
    s2cloudless_optimized.run(
        directory, resolution_resolved, output_directory=output_directory
    )
