#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Command to generate the application CMake configuration script used by the build system."""
import pathlib

import click

from mbed_tools.project import MbedProgram
from mbed_tools.build import generate_config


@click.command(
    help="Generate an Mbed OS config CMake file and write it to a .mbedbuild folder in the program directory."
)
@click.option(
    "-t",
    "--toolchain",
    type=click.Choice(["ARM", "GCC_ARM"], case_sensitive=False),
    required=True,
    help="The toolchain you are using to build your app.",
)
@click.option("-m", "--mbed-target", required=True, help="A build target for an Mbed-enabled device, eg. K64F")
@click.option(
    "-p",
    "--program-path",
    type=click.Path(),
    default=".",
    help="Path to local Mbed program. By default is the current working directory.",
)
def configure(toolchain: str, mbed_target: str, program_path: str) -> None:
    """Exports a mbed_config.cmake file to a .mbedbuild directory in the program root.

    The parameters set in the CMake file will be dependent on the combination of
    toolchain and Mbed target provided and these can then control which parts of
    Mbed OS are included in the build.

    This command will create the .mbedbuild directory at the program root if it doesn't
    exist.

    Args:
        toolchain: the toolchain you are using (eg. GCC_ARM, ARM)
        mbed_target: the target you are building for (eg. K64F)
        program_path: the path to the local Mbed program
    """
    program = MbedProgram.from_existing(pathlib.Path(program_path))
    mbed_target = mbed_target.upper()
    output_path = generate_config(mbed_target, toolchain, program)
    click.echo(f"mbed_config.cmake has been generated and written to '{str(output_path.resolve())}'")
