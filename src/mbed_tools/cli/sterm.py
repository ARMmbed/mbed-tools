#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Command to launch a serial terminal to a connected Mbed device."""
from typing import List, Any, Optional

import click

from mbed_tools.devices import get_connected_devices
from mbed_tools.devices.exceptions import MbedDevicesError
from mbed_tools.sterm import terminal


@click.command(
    help="Open a serial terminal to a connected Mbed Enabled device, or connect to a user-specified COM port."
)
@click.option(
    "-p",
    "--port",
    type=str,
    help="Communication port. Default: auto-detect. Specifying this will also ignore the -m/--mbed-target option.",
)
@click.option("-b", "--baudrate", type=int, default=9600, show_default=True, help="Communication baudrate.")
@click.option(
    "-e",
    "--echo",
    default="on",
    show_default=True,
    type=click.Choice(["on", "off"], case_sensitive=False),
    help="Switch local echo on/off.",
)
@click.option("-m", "--mbed-target", type=str, help="Mbed target to detect. Example: K64F, NUCLEO_F401RE, NRF51822...")
def sterm(port: str, baudrate: int, echo: str, mbed_target: str) -> None:
    """Launches a serial terminal to a connected device."""
    if port is None:
        port = _find_target_serial_port_or_default(_get_connected_mbed_devices(), mbed_target)

    terminal.run(port, baudrate, echo=True if echo == "on" else False)


def _get_connected_mbed_devices() -> Any:
    connected_devices = get_connected_devices()
    if not connected_devices.identified_devices:
        raise MbedDevicesError("No Mbed enabled devices found.")

    return connected_devices.identified_devices


def _find_target_serial_port_or_default(connected_devices: List, target: Optional[str]) -> Any:
    if target is None:
        # just return the first valid device found
        device, *_ = connected_devices
        return device.serial_port

    try:
        device = _find_target(connected_devices, target.upper())
    except ValueError:
        detected_targets = "\n".join(
            f"target: {dev.mbed_board.board_type}, port: {dev.serial_port}" for dev in connected_devices
        )
        msg = (
            f"Target '{target}' was not detected. Connect the device to the USB, or enter the target name correctly!\n"
            f"The following devices were detected:\n\t {detected_targets}"
        )
        raise MbedDevicesError(msg)

    return device.serial_port


def _find_target(identified_devices: List, target: str) -> Any:
    for device in identified_devices:
        if device.mbed_board.board_type == target:
            return device

    raise ValueError(f"{target} not found in {identified_devices}")
