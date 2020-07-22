#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase, mock

from mbed_tools.targets import Board
from mbed_tools.targets.exceptions import MbedTargetsError

from tests.devices.factories import CandidateDeviceFactory
from mbed_tools.devices.device import Device
from mbed_tools.devices._internal.exceptions import NoBoardForCandidate

from mbed_tools.devices.devices import get_connected_devices
from mbed_tools.devices.exceptions import DeviceLookupFailed


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
