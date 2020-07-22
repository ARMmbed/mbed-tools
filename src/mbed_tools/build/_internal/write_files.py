#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Writes out files to specified locations."""
import pathlib
from mbed_tools.build.exceptions import InvalidExportOutputDirectory


def write_file(output_directory: pathlib.Path, file_name: str, file_contents: str) -> None:
    """Writes out a file to a directory.

    If the intermediate directories to the output directory don't exist,
    this function will create them.

    This function will overwrite any existing file of the same name in the
    output directory.

    Raises:
        InvalidExportOutputDirectory: it's not possible to export to the output directory provided
    """
    if output_directory.is_file():
        raise InvalidExportOutputDirectory("Output directory cannot be a path to a file.")

    output_directory.mkdir(parents=True, exist_ok=True)
    output_file = output_directory.joinpath(file_name)
    output_file.write_text(file_contents)
