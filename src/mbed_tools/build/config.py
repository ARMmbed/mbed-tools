#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Parses the Mbed configuration system and generates a CMake config script."""
import pathlib

from mbed_tools.project import MbedProgram
from mbed_tools.targets import get_target_by_name
from mbed_tools.build._internal.cmake_file import generate_mbed_config_cmake_file
from mbed_tools.build._internal.config.assemble_build_config import assemble_config
from mbed_tools.build._internal.write_files import write_file


def generate_config(target_name: str, toolchain: str, program: MbedProgram) -> pathlib.Path:
    """Generate an Mbed config file at the program root by parsing the mbed config system.

    Args:
        target_name: Name of the target to configure for.
        toolchain: Name of the toolchain to use.
        program: The MbedProgram to configure.

    Returns:
        Path to the generated config file.
    """
    target_build_attributes = get_target_by_name(target_name, program.mbed_os.targets_json_file)
    config = assemble_config(target_build_attributes, program.root, program.files.app_config_file)
    cmake_file_contents = generate_mbed_config_cmake_file(target_name, target_build_attributes, config, toolchain)
    cmake_config_file_path = program.files.cmake_config_file
    write_file(cmake_config_file_path.parent, cmake_config_file_path.name, cmake_file_contents)
    return cmake_config_file_path
