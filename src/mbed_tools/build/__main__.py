#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Entrypoint for development purposes."""
import click

from mbed_tools.build.mbed_tools import configure


@click.group()
def cli() -> None:
    """Group exposing the commands from the mbed-build package."""
    pass


cli.add_command(configure)

cli()
