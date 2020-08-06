#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Interface for accessing Targets from Mbed OS's targets.json.

An instance of `mbed_tools.targets.target.Target`
can be retrieved by calling one of the public functions.
"""
import pathlib

from mbed_tools.targets.exceptions import TargetError
from mbed_tools.targets._internal import target_attributes


def get_target_by_name(name: str, path_to_targets_json: pathlib.Path) -> dict:
    """Returns a dictionary of attributes for the target whose name matches the name given.

    The target is as defined in the targets.json file found in the Mbed OS library.

    Args:
        name: the name of the Target to be returned
        path_to_targets_json: path to a targets.json file containing target definitions

    Raises:
        TargetError: an error has occurred while fetching target
    """
    try:
        return target_attributes.get_target_attributes(path_to_targets_json, name)
    except (FileNotFoundError, target_attributes.TargetAttributesError) as e:
        raise TargetError(e) from e


def get_target_by_board_type(board_type: str, path_to_targets_json: pathlib.Path) -> dict:
    """Returns the target whose name matches a board's build_type.

    The target is as defined in the targets.json file found in the Mbed OS library.

    Args:
        board_type: a board's board_type (see `mbed_tools.targets.board.Board`)
        path_to_targets_json: path to a targets.json file containing target definitions

    Raises:
        TargetError: an error has occurred while fetching target
    """
    return get_target_by_name(board_type, path_to_targets_json)
