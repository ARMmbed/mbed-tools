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


def assemble_config(target_attributes: dict, mbed_program_directory: Path, mbed_app_file: Optional[Path]) -> Config:
    """Assemble Config for given target and program directory.

    The structure and configuration of MbedOS requires us to do multiple passes over
    configuration files, as each pass might affect which configuration files should be included
    in the final configuration.
    """
    mbed_lib_files = find_files("mbed_lib.json", mbed_program_directory)
    return _assemble_config_from_sources_and_lib_files(target_attributes, mbed_lib_files, mbed_app_file)


def _assemble_config_from_sources_and_lib_files(
    target_attributes: dict, mbed_lib_files: Iterable[Path], mbed_app_file: Optional[Path] = None
) -> Config:
    previous_cumulative_data = None
    target_source = Source.from_target(target_attributes)
    current_cumulative_data = CumulativeData.from_sources([target_source])
    while previous_cumulative_data != current_cumulative_data:
        current_labels = current_cumulative_data.labels | current_cumulative_data.extra_labels
        filtered_files = _filter_files(
            mbed_lib_files, current_labels, current_cumulative_data.features, current_cumulative_data.components
        )
        mbed_lib_sources = [Source.from_mbed_lib(file, current_labels) for file in filtered_files]
        all_sources = [target_source] + mbed_lib_sources
        if mbed_app_file:
            all_sources = all_sources + [Source.from_mbed_app(mbed_app_file, current_labels)]

        previous_cumulative_data = current_cumulative_data
        current_cumulative_data = CumulativeData.from_sources(all_sources)

    _update_target_attributes(target_attributes, current_cumulative_data)

    return Config.from_sources(all_sources)


def _filter_files(
    files: Iterable[Path], labels: Iterable[str], features: Iterable[str], components: Iterable[str]
) -> Iterable[Path]:
    filters = (
        LabelFilter("TARGET", labels),
        LabelFilter("FEATURE", features),
        LabelFilter("COMPONENT", components),
    )
    return filter_files(files, filters)


def _update_target_attributes(target_attributes: dict, cumulative_data: CumulativeData) -> None:
    """Update target attributes with data gathered from the config system."""
    target_attributes["labels"] = cumulative_data.labels
    target_attributes["extra_labels"] = cumulative_data.extra_labels
    target_attributes["features"] = cumulative_data.features
    target_attributes["components"] = cumulative_data.components
    target_attributes["macros"] = cumulative_data.macros
