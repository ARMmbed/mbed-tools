"""Integration point with all sub-packages."""
import logging

import click

from mbed_tools_lib.logging import log_exception, set_log_level
from mbed_tools_lib.exceptions import ToolsError

from mbed_devices.mbed_tools import cli as mbed_devices_cli
from mbed_tools._internal.config_cli import cli as config_cli


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
LOGGER = logging.getLogger(__name__)


class GroupWithExceptionHandling(click.Group):
    """A click.Group which handles ToolsErrors and logging."""

    def invoke(self, context: click.Context) -> None:
        """Invoke the command group.

        Args:
            context: The current click context.
        """
        try:
            super().invoke(context)
        except ToolsError as err:
            traceback = context.params["traceback"]
            if LOGGER.level != logging.DEBUG and not traceback:
                err = (
                    f"{err}\nIncrease the verbosity level to `-vvv` to see debug information."
                    " Use the `--traceback` argument to see a full stack trace."
                )
            log_exception(LOGGER, err, traceback)


@click.group(cls=GroupWithExceptionHandling, context_settings=CONTEXT_SETTINGS)
@click.option(
    "-v",
    "--verbose",
    default=0,
    count=True,
    help="Set the verbosity level, enter multiple times to increase verbosity.",
)
@click.option("-t", "--traceback", is_flag=True, show_default=True, help="Show a traceback when an error is raised.")
def cli(verbose: int, traceback: bool) -> None:
    """Command line tool for interacting with Mbed OS."""
    set_log_level(verbose)


cli.add_command(mbed_devices_cli, "devices")
cli.add_command(config_cli, "config")
