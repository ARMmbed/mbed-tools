#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Command to generate the application CMake configuration script used by the build system."""
import pathlib

import click

from typing import Any

from mbed_tools.build._internal.cmake_file import generate_mbed_config_cmake_file
from mbed_tools.build._internal.write_files import write_file


@click.command(
    help="Generate an Mbed OS config CMake file and write it to a .mbedbuild folder in the program directory."
)
@click.option(
    "-o",
    "--output-directory",
    type=click.Path(),
    default=".",
    help=(
        "Destination for the generated .mbedbuild/mbed_config.cmake file containing configuration parameters to build "
        "Mbed OS. The default is the current working directory."
    ),
)
@click.option(
    "-t",
    "--toolchain",
    type=click.Choice(["ARM", "GCC_ARM"]),
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
def configure(output_directory: Any, toolchain: str, mbed_target: str, program_path: str) -> None:
    """Exports a mbed_config.cmake file to a .mbedbuild directory in the output path.

    The parameters set in the CMake file will be dependent on the combination of
    toolchain and Mbed target provided and these can then control which parts of
    Mbed OS are included in the build.

    This command will create the .mbedbuild directory at the output path if it doesn't
    exist.

    Args:
        output_directory: the path where .mbedbuild/mbed_config.cmake will be written
        toolchain: the toolchain you are using (eg. GCC_ARM, ARM)
        mbed_target: the target you are building for (eg. K64F)
        program_path: the path to the local Mbed program
    """
    cmake_file_contents = generate_mbed_config_cmake_file(mbed_target.upper(), pathlib.Path(program_path), toolchain)
    output_directory = pathlib.Path(output_directory, ".mbedbuild")
    write_file(output_directory, "mbed_config.cmake", cmake_file_contents)
    click.echo(f"mbed_config.cmake has been generated and written to '{str(output_directory.resolve())}'")
