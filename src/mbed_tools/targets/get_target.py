#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Interface for accessing Targets from Mbed OS's targets.json.

An instance of `mbed_tools.targets.target.Target`
can be retrieved by calling one of the public functions.
"""
import pathlib

from mbed_tools.targets.target import Target
from mbed_tools.project import MbedProgram


def get_target_by_name(name: str, path_to_mbed_program: pathlib.Path) -> Target:
    """Returns the Target whose name matches the name given.

    The Target is as defined in the targets.json file found in the Mbed OS library.
    The program whose path is provided here will need a valid copy of the Mbed OS library
    in order to access this file.

    Args:
        name: the name of the Target to be returned
        path_to_mbed_program: path to an Mbed OS program

    Raises:
        TargetError: an error has occurred while fetching target
    """
    mbed_program = MbedProgram.from_existing(pathlib.Path(path_to_mbed_program))
    path_to_targets_json = mbed_program.mbed_os.targets_json_file
    return Target.from_targets_json(name, path_to_targets_json)


def get_target_by_board_type(board_type: str, path_to_mbed_program: pathlib.Path) -> Target:
    """Returns the Target whose name matches a board's build_type.

    The Target is as defined in the targets.json file found in the Mbed OS library.
    The program whose path is provided here will need a valid copy of the Mbed OS library
    in order to access this file.

    Args:
        board_type: a board's board_type (see `mbed_tools.targets.board.Board`)
        path_to_mbed_program: path to an Mbed OS program

    Raises:
        TargetError: an error has occurred while fetching target
    """
    return get_target_by_name(board_type, path_to_mbed_program)
