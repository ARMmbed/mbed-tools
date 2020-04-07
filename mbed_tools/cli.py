#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Integration point with all sub-packages."""
import logging

import click

from mbed_tools_lib.logging import set_log_level, MbedToolsHandler

from mbed_build.mbed_tools import cli as mbed_build_export_cli
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
        # Use the context manager to ensure tools exceptions (expected behaviour) are shown as messages to the user,
        # but all other exceptions (unexpected behaviour) are shown as errors.
        with MbedToolsHandler(LOGGER, context.params["traceback"]):
            super().invoke(context)


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


cli.add_command(mbed_build_export_cli, "export")
cli.add_command(mbed_devices_cli, "devices")
cli.add_command(config_cli, "config")
