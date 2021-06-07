#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Command to generate the application CMake configuration script used by the build/compile system."""
import pathlib

import click

from mbed_tools.project import MbedProgram
from mbed_tools.build import generate_config


@click.command(
    help="Generate an Mbed OS config CMake file and write it to a .mbedbuild folder in the program directory."
)
@click.option(
    "--custom-targets-json", type=click.Path(), default=None, help="Path to custom_targets.json.",
)
@click.option(
    "-t",
    "--toolchain",
    type=click.Choice(["ARM", "GCC_ARM"], case_sensitive=False),
    required=True,
    help="The toolchain you are using to build your app.",
)
@click.option("-m", "--mbed-target", required=True, help="A build target for an Mbed-enabled device, eg. K64F")
@click.option("-o", "--output-dir", type=click.Path(), default=None, help="Path to output directory.")
@click.option(
    "-p",
    "--program-path",
    type=click.Path(),
    default=".",
    help="Path to local Mbed program. By default is the current working directory.",
)
@click.option(
    "--mbed-os-path", type=click.Path(), default=None, help="Path to local Mbed OS directory.",
)
def configure(
    toolchain: str, mbed_target: str, program_path: str, mbed_os_path: str, output_dir: str, custom_targets_json: str
) -> None:
    """Exports a mbed_config.cmake file to build directory in the program root.

    The parameters set in the CMake file will be dependent on the combination of
    toolchain and Mbed target provided and these can then control which parts of
    Mbed OS are included in the build.

    This command will create the .mbedbuild directory at the program root if it doesn't
    exist.

    Args:
        custom_targets_json: the path to custom_targets.json
        toolchain: the toolchain you are using (eg. GCC_ARM, ARM)
        mbed_target: the target you are building for (eg. K64F)
        program_path: the path to the local Mbed program
        mbed_os_path: the path to the local Mbed OS directory
        output_dir: the path to the output directory
    """
    cmake_build_subdir = pathlib.Path(mbed_target.upper(), "develop", toolchain.upper())
    if mbed_os_path is None:
        program = MbedProgram.from_existing(pathlib.Path(program_path), cmake_build_subdir)
    else:
        program = MbedProgram.from_existing(pathlib.Path(program_path), cmake_build_subdir, pathlib.Path(mbed_os_path))
    if custom_targets_json is not None:
        program.files.custom_targets_json = pathlib.Path(custom_targets_json)
    if output_dir is not None:
        program.files.cmake_build_dir = pathlib.Path(output_dir)

    mbed_target = mbed_target.upper()
    _, output_path = generate_config(mbed_target, toolchain, program)
    click.echo(f"mbed_config.cmake has been generated and written to '{str(output_path.resolve())}'")
