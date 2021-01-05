#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""API for listing devices."""

from typing import Optional

from mbed_tools.targets.exceptions import MbedTargetsError
from mbed_tools.targets import Board

from mbed_tools.devices._internal.detect_candidate_devices import detect_candidate_devices
from mbed_tools.devices._internal.resolve_board import resolve_board
from mbed_tools.devices._internal.exceptions import NoBoardForCandidate

from mbed_tools.devices.device import ConnectedDevices, Device
from mbed_tools.devices.exceptions import DeviceLookupFailed, NoDevicesFound


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


def find_connected_device(target_name: str) -> Device:
    """Find a connected device matching the given target_name.

    Args:
        target_name: The Mbed target name of the device.

    Raises:
        NoDevicesFound: Could not find any connected devices.
        DeviceLookupFailed: Could not find a connected device matching target_name.

    Returns:
        Device matching target_name.
    """
    connected = get_connected_devices()
    if not connected.identified_devices:
        raise NoDevicesFound("No Mbed enabled devices found.")

    for device in connected.identified_devices:
        if device.mbed_board.board_type == target_name.upper():
            return device

    detected_targets = "\n".join(
        f"target: {dev.mbed_board.board_type}, port: {dev.serial_port}, mount point(s): {dev.mount_points}"
        for dev in connected.identified_devices
    )
    msg = (
        f"Target '{target_name}' was not detected. Connect the device to the USB, or enter the target name correctly!\n"
        f"The following devices were detected:\n\t {detected_targets}"
    )
    raise DeviceLookupFailed(msg)
