#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Configuration assembly algorithm."""
from pathlib import Path
from typing import Iterable, Optional

from mbed_tools.build._internal.config.config import Config
from mbed_tools.build._internal.config.cumulative_data import CumulativeData
from mbed_tools.build._internal.config.source import Source
from mbed_tools.build._internal.find_files import LabelFilter, filter_files, find_files
from mbed_tools.project import MbedProgram


def assemble_config(mbed_target: str, mbed_program_directory: Path) -> Config:
    """Assemble Config for given target and program directory.

    The structure and configuration of MbedOS requires us to do multiple passes over
    configuration files, as each pass might affect which configuration files should be included
    in the final configuration.
    """
    target_source = Source.from_target(mbed_target, mbed_program_directory)
    mbed_lib_files = find_files("mbed_lib.json", mbed_program_directory)
    mbed_program = MbedProgram.from_existing(mbed_program_directory)
    mbed_app_file = mbed_program.files.app_config_file
    return _assemble_config_from_sources_and_lib_files(target_source, mbed_lib_files, mbed_app_file)


def _assemble_config_from_sources_and_lib_files(
    target_source: Source, mbed_lib_files: Iterable[Path], mbed_app_file: Optional[Path] = None
) -> Config:
    previous_cumulative_data = None
    current_cumulative_data = CumulativeData.from_sources([target_source])
    while previous_cumulative_data != current_cumulative_data:
        filtered_files = _filter_files(mbed_lib_files, current_cumulative_data)
        mbed_lib_sources = [Source.from_mbed_lib(file, current_cumulative_data.labels) for file in filtered_files]
        all_sources = [target_source] + mbed_lib_sources
        if mbed_app_file:
            all_sources = all_sources + [Source.from_mbed_app(mbed_app_file, current_cumulative_data.labels)]
        previous_cumulative_data = current_cumulative_data
        current_cumulative_data = CumulativeData.from_sources(all_sources)

    return Config.from_sources(all_sources)


def _filter_files(files: Iterable[Path], cumulative_data: CumulativeData) -> Iterable[Path]:
    filters = (
        LabelFilter("TARGET", cumulative_data.labels),
        LabelFilter("FEATURE", cumulative_data.features),
        LabelFilter("COMPONENT", cumulative_data.components),
    )
    return filter_files(files, filters)
