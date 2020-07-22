#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase, mock

from tests.devices.markers import windows_only, darwin_only, linux_only
from mbed_tools.devices._internal.base_detector import DeviceDetector
from mbed_tools.devices._internal.detect_candidate_devices import (
    detect_candidate_devices,
    _get_detector_for_current_os,
)


class TestDetectCandidateDevices(TestCase):
    @mock.patch("mbed_tools.devices._internal.detect_candidate_devices._get_detector_for_current_os")
    def test_returns_candidates_using_os_specific_detector(self, _get_detector_for_current_os):
        detector = mock.Mock(spec_set=DeviceDetector)
        _get_detector_for_current_os.return_value = detector
        self.assertEqual(detect_candidate_devices(), detector.find_candidates.return_value)


class TestGetDetectorForCurrentOS(TestCase):
    @windows_only
    def test_windows_uses_correct_module(self):
        from mbed_tools.devices._internal.windows.device_detector import WindowsDeviceDetector

        self.assertIsInstance(_get_detector_for_current_os(), WindowsDeviceDetector)

    @darwin_only
    def test_darwin_uses_correct_module(self):
        from mbed_tools.devices._internal.darwin.device_detector import DarwinDeviceDetector

        self.assertIsInstance(_get_detector_for_current_os(), DarwinDeviceDetector)

    @linux_only
    def test_linux_uses_correct_module(self):
        from mbed_tools.devices._internal.linux.device_detector import LinuxDeviceDetector

        self.assertIsInstance(_get_detector_for_current_os(), LinuxDeviceDetector)
