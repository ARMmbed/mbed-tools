#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Command to list all Mbed enabled devices connected to the host computer."""
import click
import json
from operator import attrgetter
from typing import Iterable
from tabulate import tabulate

from mbed_tools.devices import get_connected_devices, Device
from mbed_tools.targets import Board


@click.command()
@click.option(
    "--format", type=click.Choice(["table", "json"]), default="table", show_default=True, help="Set output format."
)
@click.option(
    "--show-all",
    "-a",
    is_flag=True,
    default=False,
    help="Show all connected devices, even those which are not Mbed Boards.",
)
def list_connected_devices(format: str, show_all: bool) -> None:
    """Prints connected devices."""
    connected_devices = get_connected_devices()

    if show_all:
        devices = _sort_devices(connected_devices.identified_devices + connected_devices.unidentified_devices)
    else:
        devices = _sort_devices(connected_devices.identified_devices)

    output_builders = {
        "table": _build_tabular_output,
        "json": _build_json_output,
    }
    if devices:
        output = output_builders[format](devices)
        click.echo(output)
    else:
        click.echo("No connected Mbed devices found.")


def _sort_devices(devices: Iterable[Device]) -> Iterable[Device]:
    """Sort devices by board name and then serial number (in case there are multiple boards with the same name)."""
    return sorted(devices, key=attrgetter("mbed_board.board_name", "serial_number"))


def _build_tabular_output(devices: Iterable[Device]) -> str:
    headers = ["Board name", "Serial number", "Serial port", "Mount point(s)", "Build target(s)"]
    devices_data = []
    for device in devices:
        devices_data.append(
            [
                device.mbed_board.board_name or "<unknown>",
                device.serial_number,
                device.serial_port or "<unknown>",
                "\n".join(str(mount_point) for mount_point in device.mount_points),
                "\n".join(_get_build_targets(device.mbed_board)),
            ]
        )
    return tabulate(devices_data, headers=headers)


def _build_json_output(devices: Iterable[Device]) -> str:
    devices_data = []
    for device in devices:
        board = device.mbed_board
        devices_data.append(
            {
                "serial_number": device.serial_number,
                "serial_port": device.serial_port,
                "mount_points": [str(m) for m in device.mount_points],
                "mbed_board": {
                    "product_code": board.product_code,
                    "board_type": board.board_type,
                    "board_name": board.board_name,
                    "mbed_os_support": board.mbed_os_support,
                    "mbed_enabled": board.mbed_enabled,
                    "build_targets": _get_build_targets(board),
                },
            }
        )
    return json.dumps(devices_data, indent=4)


def _get_build_targets(board: Board) -> Iterable[str]:
    return [f"{board.board_type}_{variant}" for variant in board.build_variant] + [board.board_type]
