#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Command to build an Mbed project using CMake."""
import os
import pathlib

import click

from mbed_tools.build import build_project, generate_build_system, generate_config
from mbed_tools.project import MbedProgram


@click.command(name="build", help="Build an Mbed project.")
@click.option(
    "-t",
    "--toolchain",
    type=click.Choice(["ARM", "GCC_ARM"], case_sensitive=False),
    help="The toolchain you are using to build your app.",
)
@click.option("-m", "--mbed-target", help="A build target for an Mbed-enabled device, e.g. K64F.")
@click.option("-b", "--build-type", default="develop", help="The build type (release, develop or debug).")
@click.option("-c", "--clean", is_flag=True, default=False, help="Perform a 'clean' build.")
@click.option(
    "-p",
    "--program-path",
    default=os.getcwd(),
    help="Path to local Mbed program. By default it is the current working directory.",
)
def build(program_path: str, build_type: str, toolchain: str = "", mbed_target: str = "", clean: bool = False) -> None:
    """Configure and build an Mbed project using CMake and Ninja.

    If the project has already been configured and contains '.mbedbuild/mbed_config.cmake', this command will skip the
    Mbed configuration step and invoke CMake.

    If the CMake configuration step has already been run previously (i.e a CMake build tree exists), then just try to
    build the project immediately using Ninja.

    Args:
       program_path: Path to the Mbed project.
       build_type: The Mbed build profile (debug, develop or release).
       toolchain: The toolchain to use for the build.
       mbed_target: The name of the Mbed target to build for.
       clean: Force regeneration of config and build system before building.
    """
    program = MbedProgram.from_existing(pathlib.Path(program_path))
    mbed_config_file = program.files.cmake_config_file
    if not mbed_config_file.exists() or clean:
        click.echo("Generating Mbed config...")
        if not toolchain:
            raise click.UsageError("--toolchain argument is required when generating Mbed config!")

        if not mbed_target:
            raise click.UsageError("--mbed-target argument is required when generating Mbed config!")

        generate_config(mbed_target.upper(), toolchain, program)

    build_tree = program.files.cmake_build_dir
    if not build_tree.exists() or clean:
        generate_build_system(program.root, build_tree, build_type)

    build_project(build_tree)
