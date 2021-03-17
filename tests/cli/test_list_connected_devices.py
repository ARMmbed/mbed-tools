#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import pathlib
import pytest
from click.testing import CliRunner
from mbed_tools.devices.device import ConnectedDevices
from mbed_tools.targets import Board
from tabulate import tabulate
from unittest import mock

from mbed_tools.cli.list_connected_devices import (
    list_connected_devices,
    _build_tabular_output,
    _build_json_output,
    _get_build_targets,
    _sort_devices,
)
from mbed_tools.devices import Device

identified_devices = [mock.Mock(spec_set=Device)]
unidentified_devices = [mock.Mock(spec_set=Device)]


@pytest.fixture
def get_connected_devices():
    with mock.patch("mbed_tools.cli.list_connected_devices.get_connected_devices") as cd:
        cd.return_value = ConnectedDevices(
            identified_devices=identified_devices, unidentified_devices=unidentified_devices
        )
        yield cd


@pytest.fixture
def _sort_devices_mock():
    with mock.patch("mbed_tools.cli.list_connected_devices._sort_devices") as sd:
        yield sd


@pytest.fixture
def _build_tabular_output_mock():
    with mock.patch("mbed_tools.cli.list_connected_devices._build_tabular_output") as bto:
        yield bto


@pytest.fixture
def _build_json_output_mock():
    with mock.patch("mbed_tools.cli.list_connected_devices._build_json_output") as bjo:
        yield bjo


class TestListConnectedDevices:
    def test_informs_when_no_devices_are_connected(self, get_connected_devices):
        get_connected_devices.return_value = ConnectedDevices()

        result = CliRunner().invoke(list_connected_devices)

        assert result.exit_code == 0
        assert "No connected Mbed devices found." in result.output

    def test_by_default_lists_devices_using_tabular_output(
        self, _build_tabular_output_mock, _sort_devices_mock, get_connected_devices
    ):
        _build_tabular_output_mock.return_value = "some output"

        result = CliRunner().invoke(list_connected_devices)

        assert result.exit_code == 0
        assert _build_tabular_output_mock.return_value in result.output
        _build_tabular_output_mock.assert_called_once_with(_sort_devices_mock.return_value)
        _sort_devices_mock.assert_called_once_with(identified_devices)

    def test_given_json_flag_lists_devices_using_json_output(
        self, _build_json_output_mock, _sort_devices_mock, get_connected_devices
    ):
        _build_json_output_mock.return_value = "some output"

        result = CliRunner().invoke(list_connected_devices, "--format=json")

        assert result.exit_code == 0
        assert _build_json_output_mock.return_value in result.output
        _build_json_output_mock.assert_called_once_with(_sort_devices_mock.return_value)
        _sort_devices_mock.assert_called_once_with(identified_devices)

    def test_given_show_all(self, _build_tabular_output_mock, _sort_devices_mock, get_connected_devices):
        _build_tabular_output_mock.return_value = "some output"

        result = CliRunner().invoke(list_connected_devices, "--show-all")

        assert result.exit_code == 0
        assert _build_tabular_output_mock.return_value in result.output
        _build_tabular_output_mock.assert_called_once_with(_sort_devices_mock.return_value)
        _sort_devices_mock.assert_called_once_with(identified_devices + unidentified_devices)


class TestSortDevices:
    def test_sorts_devices_by_board_name(self):
        device_1 = mock.create_autospec(
            Device, mbed_board=mock.create_autospec(Board, board_name="A"), serial_number="123"
        )
        device_2 = mock.create_autospec(
            Device, mbed_board=mock.create_autospec(Board, board_name="B"), serial_number="456"
        )
        device_3 = mock.create_autospec(
            Device, mbed_board=mock.create_autospec(Board, board_name="C"), serial_number="789"
        )

        result = _sort_devices([device_3, device_1, device_2])

        assert list(result) == [device_1, device_2, device_3]

    def test_sorts_devices_by_serial_number(self):
        device_1 = mock.create_autospec(
            Device, mbed_board=mock.create_autospec(Board, board_name=""), serial_number="123"
        )
        device_2 = mock.create_autospec(
            Device, mbed_board=mock.create_autospec(Board, board_name=""), serial_number="456"
        )
        device_3 = mock.create_autospec(
            Device, mbed_board=mock.create_autospec(Board, board_name=""), serial_number="789"
        )

        result = _sort_devices([device_3, device_1, device_2])

        assert list(result) == [device_1, device_2, device_3]

    def test_sorts_devices_by_board_name_then_serial_number(self):
        device_1 = mock.create_autospec(
            Device, mbed_board=mock.create_autospec(Board, board_name=""), serial_number="123"
        )
        device_2 = mock.create_autospec(
            Device, mbed_board=mock.create_autospec(Board, board_name="Mbed"), serial_number="456"
        )
        device_3 = mock.create_autospec(
            Device, mbed_board=mock.create_autospec(Board, board_name=""), serial_number="789"
        )

        result = _sort_devices([device_3, device_1, device_2])

        assert list(result) == [device_1, device_3, device_2]


class TestBuildTableOutput:
    def test_returns_tabularised_representation_of_devices(self):
        device = Device(
            mbed_board=mock.create_autospec(
                Board, board_name="board-name", build_variant=("S", "NS"), board_type="board-type",
            ),
            serial_number="serial-number",
            serial_port="serial-port",
            mount_points=[pathlib.Path("/Volumes/FOO"), pathlib.Path("/Volumes/BAR")],
        )

        output = _build_tabular_output([device])

        expected_output = tabulate(
            [
                [
                    device.mbed_board.board_name,
                    device.serial_number,
                    device.serial_port,
                    "\n".join(map(str, device.mount_points)),
                    "\n".join(_get_build_targets(device.mbed_board, None)),
                ]
            ],
            headers=["Board name", "Serial number", "Serial port", "Mount point(s)", "Build target(s)"],
        )
        assert output == expected_output

    def test_returns_tabularised_with_identifier(self):
        board = mock.create_autospec(
            Board, board_name="board-name", build_variant=("S", "NS"), board_type="board-type",
        )
        device = Device(
            mbed_board=board,
            serial_number="123",
            serial_port="serial-port",
            mount_points=[pathlib.Path("/Volumes/FOO"), pathlib.Path("/Volumes/BAR")],
        )
        device_2 = Device(
            mbed_board=board,
            serial_number="456",
            serial_port="serial-port",
            mount_points=[pathlib.Path("/Volumes/FOO"), pathlib.Path("/Volumes/BAR")],
        )

        output = _build_tabular_output([device, device_2])

        expected_output = tabulate(
            [
                [
                    f"{device.mbed_board.board_name}",
                    device.serial_number,
                    device.serial_port,
                    "\n".join(map(str, device.mount_points)),
                    "\n".join(_get_build_targets(board, 0)),
                ],
                [
                    f"{device_2.mbed_board.board_name}",
                    device_2.serial_number,
                    device_2.serial_port,
                    "\n".join(map(str, device_2.mount_points)),
                    "\n".join(_get_build_targets(board, 1)),
                ],
            ],
            headers=["Board name", "Serial number", "Serial port", "Mount point(s)", "Build target(s)"],
        )
        assert output == expected_output

    def test_displays_unknown_serial_port_value(self):
        device = Device(
            mbed_board=Board.from_offline_board_entry({}),
            serial_number="serial",
            serial_port=None,
            mount_points=[pathlib.Path("somepath")],
        )

        output = _build_tabular_output([device])

        expected_output = tabulate(
            [
                [
                    "<unknown>",
                    device.serial_number,
                    "<unknown>",
                    "\n".join(map(str, device.mount_points)),
                    "\n".join(_get_build_targets(device.mbed_board, None)),
                ]
            ],
            headers=["Board name", "Serial number", "Serial port", "Mount point(s)", "Build target(s)"],
        )
        assert output == expected_output


class TestBuildJsonOutput:
    def test_returns_json_representation_of_devices(self):
        board = mock.create_autospec(
            Board,
            product_code="0021",
            board_type="HAT-BOAT",
            board_name="HAT Boat",
            mbed_os_support=["0.2"],
            mbed_enabled=["potentially"],
            build_variant=("S", "NS"),
        )
        device = Device(
            mbed_board=board, serial_number="09887654", serial_port="COM1", mount_points=[pathlib.Path("somepath")],
        )

        output = _build_json_output([device])
        expected_output = json.dumps(
            [
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
                        "build_targets": _get_build_targets(board, None),
                    },
                }
            ],
            indent=4,
        )

        assert output == expected_output

    def test_returns_json_representation_with_identifier(self):
        board = mock.create_autospec(
            Board,
            product_code="0021",
            board_type="HAT-BOAT",
            board_name="HAT Boat",
            mbed_os_support=["0.2"],
            mbed_enabled=["potentially"],
            build_variant=("S", "NS"),
        )
        device = Device(
            mbed_board=board, serial_number="09887654", serial_port="COM1", mount_points=[pathlib.Path("somepath")],
        )
        device_2 = Device(
            mbed_board=board, serial_number="09884321", serial_port="COM2", mount_points=[pathlib.Path("anotherpath")],
        )

        output = _build_json_output([device, device_2])
        expected_output = json.dumps(
            [
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
                        "build_targets": _get_build_targets(board, 0),
                    },
                },
                {
                    "serial_number": device_2.serial_number,
                    "serial_port": device_2.serial_port,
                    "mount_points": [str(m) for m in device_2.mount_points],
                    "mbed_board": {
                        "product_code": board.product_code,
                        "board_type": board.board_type,
                        "board_name": board.board_name,
                        "mbed_os_support": board.mbed_os_support,
                        "mbed_enabled": board.mbed_enabled,
                        "build_targets": _get_build_targets(board, 1),
                    },
                },
            ],
            indent=4,
        )

        assert output == expected_output

    def test_empty_values_keys_are_always_present(self):
        """Asserts that keys are present even if value is None."""
        device = Device(
            mbed_board=Board.from_offline_board_entry({}), serial_number="foo", serial_port=None, mount_points=[],
        )

        output = json.loads(_build_json_output([device]))

        assert output[0]["serial_port"] is None


class TestGetBuildTargets:
    def test_returns_base_target_and_all_variants(self):
        board = mock.create_autospec(Board, build_variant=("S", "NS"), board_type="FOO")

        assert _get_build_targets(board, None) == ["FOO_S", "FOO_NS", "FOO"]

    def test_returns_base_and_variants_identifier(self):
        board = mock.create_autospec(Board, build_variant=("S", "NS"), board_type="FOO")
        assert _get_build_targets(board, 2) == ["FOO_S[2]", "FOO_NS[2]", "FOO[2]"]
