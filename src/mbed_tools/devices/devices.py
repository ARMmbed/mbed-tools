#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""API for listing devices."""

from typing import Optional

from mbed_tools.targets.exceptions import MbedTargetsError
from mbed_tools.targets import Board

from mbed_tools.devices._internal.detect_candidate_devices import detect_candidate_devices
from mbed_tools.devices._internal.resolve_board import resolve_board
from mbed_tools.devices._internal.exceptions import NoBoardForCandidate

from mbed_tools.devices.device import ConnectedDevices
from mbed_tools.devices.exceptions import DeviceLookupFailed


def get_connected_devices() -> ConnectedDevices:
    """Returns Mbed Devices connected to host computer.

    Connected devices which have been identified as Mbed Boards and also connected devices which are potentially
    Mbed Boards (but not could not be identified in the database) are returned.

    Raises:
        DeviceLookupFailed: If there is a problem with the process of identifying Mbed Boards from connected devices.
    """
    connected_devices = ConnectedDevices()

    board: Optional["Board"]
    for candidate_device in detect_candidate_devices():
        try:
            board = resolve_board(candidate_device)
        except NoBoardForCandidate:
            board = None
        except MbedTargetsError as err:
            raise DeviceLookupFailed("A problem occurred when looking up board data for connected devices.") from err

        connected_devices.add_device(candidate_device, board)

    return connected_devices
