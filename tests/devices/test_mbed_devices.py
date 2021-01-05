#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib
import re

from unittest import TestCase, mock

from mbed_tools.targets import Board
from mbed_tools.targets.exceptions import MbedTargetsError

from tests.devices.factories import CandidateDeviceFactory
from mbed_tools.devices.device import Device
from mbed_tools.devices._internal.exceptions import NoBoardForCandidate

from mbed_tools.devices.devices import get_connected_devices, find_connected_device
from mbed_tools.devices.exceptions import DeviceLookupFailed, NoDevicesFound


@mock.patch("mbed_tools.devices.devices.detect_candidate_devices")
@mock.patch("mbed_tools.devices.devices.resolve_board")
class TestGetConnectedDevices(TestCase):
    def test_builds_devices_from_candidates(self, resolve_board, detect_candidate_devices):
        candidate = CandidateDeviceFactory()
        detect_candidate_devices.return_value = [candidate]

        connected_devices = get_connected_devices()
        self.assertEqual(
            connected_devices.identified_devices,
            [
                Device(
                    serial_port=candidate.serial_port,
                    serial_number=candidate.serial_number,
                    mount_points=candidate.mount_points,
                    mbed_board=resolve_board.return_value,
                )
            ],
        )
        self.assertEqual(connected_devices.unidentified_devices, [])
        resolve_board.assert_called_once_with(candidate)

    @mock.patch.object(Board, "from_offline_board_entry")
    def test_skips_candidates_without_a_board(self, board, resolve_board, detect_candidate_devices):
        candidate = CandidateDeviceFactory()
        resolve_board.side_effect = NoBoardForCandidate
        detect_candidate_devices.return_value = [candidate]
        board.return_value = None

        connected_devices = get_connected_devices()
        self.assertEqual(connected_devices.identified_devices, [])
        self.assertEqual(
            connected_devices.unidentified_devices,
            [
                Device(
                    serial_port=candidate.serial_port,
                    serial_number=candidate.serial_number,
                    mount_points=candidate.mount_points,
                    mbed_board=None,
                )
            ],
        )

    def test_raises_device_lookup_failed_on_internal_error(self, resolve_board, detect_candidate_devices):
        resolve_board.side_effect = MbedTargetsError
        detect_candidate_devices.return_value = [CandidateDeviceFactory()]

        with self.assertRaises(DeviceLookupFailed):
            get_connected_devices()


@mock.patch("mbed_tools.devices.devices.get_connected_devices")
class TestFindConnectedDevice(TestCase):
    def test_finds_device_with_matching_name(self, mock_get_connected_devices):
        target_name = "K64F"
        mock_get_connected_devices.return_value = mock.Mock(
            identified_devices=[mock.Mock(mbed_board=mock.Mock(board_type=target_name, spec=True), spec=True)],
            spec=True,
        )

        dev = find_connected_device(target_name)

        self.assertEqual(target_name, dev.mbed_board.board_type)

    def test_raises_when_no_mbed_enabled_devices_found(self, mock_get_connected_devices):
        mock_get_connected_devices.return_value = mock.Mock(identified_devices=[], spec=True)

        with self.assertRaises(NoDevicesFound):
            find_connected_device("K64F")

    def test_raises_when_device_matching_target_name_not_found(self, mock_get_connected_devices):
        target_name = "K64F"
        connected_target_name = "DISCO"
        connected_target_serial_port = "tty.BLEH"
        connected_target_mount_point = [pathlib.Path("/dap")]
        mock_get_connected_devices.return_value = mock.Mock(
            identified_devices=[
                mock.Mock(
                    serial_port=connected_target_serial_port,
                    mount_points=connected_target_mount_point,
                    mbed_board=mock.Mock(board_type=connected_target_name, spec=True),
                    spec=True,
                )
            ],
            spec=True,
        )

        with self.assertRaisesRegex(
            DeviceLookupFailed,
            f".*(target: {re.escape(connected_target_name)}).*(port: {re.escape(connected_target_serial_port)}).*"
            f"(mount point.*: {re.escape(str(connected_target_mount_point))})",
        ):
            find_connected_device(target_name)
