#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Data model definition for Device and ConnectedDevices."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple, Optional, List
from mbed_tools.targets import Board
from mbed_tools.devices._internal.detect_candidate_devices import CandidateDevice


@dataclass(frozen=True, order=True)
class Device:
    """Definition of an Mbed Enabled Device.

    An Mbed Device is always a USB mass storage device, which sometimes also presents a USB serial port.
    A valid Mbed Device must have a Board associated with it.

    Attributes:
        mbed_board: The Board associated with this device.
        serial_number: The serial number presented by the device to the USB subsystem.
        serial_port: The serial port presented by this device, could be None.
        mount_points: The filesystem mount points associated with this device.
    """

    mbed_board: Board
    serial_number: str
    serial_port: Optional[str]
    mount_points: Tuple[Path, ...]


@dataclass(order=True)
class ConnectedDevices:
    """Definition of connected devices which may be Mbed Boards.

    If a connected device is identified as an Mbed Board by using the HTM file on the USB mass storage device (or
    sometimes by using the serial number), it will be included in the `identified_devices` list.

    However, if the device appears as if it could be an Mbed Board but it has not been possible to find a matching
    entry in the database then it will be included in the `unidentified_devices` list.

    Attributes:
        identified_devices: A list of devices that have been identified as MbedTargets.
        unidentified_devices: A list of devices that could potentially be MbedTargets.
    """

    identified_devices: List[Device] = field(default_factory=list)
    unidentified_devices: List[Device] = field(default_factory=list)

    def add_device(self, candidate_device: CandidateDevice, mbed_board: Optional[Board] = None) -> None:
        """Add a candidate device and optionally an Mbed Target to the connected devices.

        Args:
            candidate_device: a CandidateDevice object containing the device information.
            mbed_board: a Board object for identified devices, for unidentified devices this will be None.
        """
        new_device = Device(
            serial_port=candidate_device.serial_port,
            serial_number=candidate_device.serial_number,
            mount_points=candidate_device.mount_points,
            # Create an empty Board to ensure the device is fully populated and rendering is simple
            mbed_board=mbed_board if mbed_board is not None else Board.from_offline_board_entry({}),
        )

        if mbed_board is None:
            # Keep a list of devices that could not be identified but are Mbed Boards
            self.unidentified_devices.append(new_device)
        else:
            # Keep a list of devices that have been identified as Mbed Boards
            self.identified_devices.append(new_device)
