#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Command to build an Mbed project using CMake."""
import os
import pathlib
import shutil

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
@click.option("-c", "--clean", is_flag=True, default=False, help="Perform a clean build.")
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
       clean: Perform a clean build.
    """
    program = MbedProgram.from_existing(pathlib.Path(program_path))
    mbed_config_file = program.files.cmake_config_file
    build_tree = program.files.cmake_build_dir
    if clean and build_tree.exists():
        shutil.rmtree(build_tree)

    if any([not mbed_config_file.exists(), not build_tree.exists(), mbed_target, toolchain]):
        click.echo("Configuring project and generating build system...")
        _validate_target_and_toolchain_args(mbed_target, toolchain)
        generate_config(mbed_target.upper(), toolchain, program)
        generate_build_system(program.root, build_tree, build_type)

    click.echo("Building Mbed project...")
    build_project(build_tree)


def _validate_target_and_toolchain_args(target: str, toolchain: str) -> None:
    if not all([toolchain, target]):
        raise click.UsageError("--toolchain and --mbed-target arguments are required when generating Mbed config!")
