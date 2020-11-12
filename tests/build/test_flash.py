#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import pathlib
import tempfile

from unittest import TestCase, mock

from mbed_tools.devices.device import ConnectedDevices
from mbed_tools.build.flash import flash_binary, _build_binary_file_path, _find_connected_device, _flash_dev
from mbed_tools.build.exceptions import BinaryFileNotFoundError, DeviceNotFoundError

from tests.build.factories import DeviceFactory, ConnectedDevicesFactory


@mock.patch("mbed_tools.build.flash._find_connected_device")
@mock.patch("mbed_tools.build.flash._build_binary_file_path")
@mock.patch("mbed_tools.build.flash._flash_dev")
class TestFlashBinary(TestCase):
    def test_check_flashing(self, _flash_dev, _build_binary_file_path, _find_connected_device):
        test_device = DeviceFactory()

        _find_connected_device.return_value = test_device
        _flash_dev.return_value = True

        with tempfile.TemporaryDirectory() as tmpDir:
            base_dir = pathlib.Path(tmpDir)
            build_dir = base_dir / "cmake_build"
            build_dir.mkdir()
            bin_file = base_dir.name + ".bin"
            bin_file = build_dir / bin_file
            bin_file.touch()
            _build_binary_file_path.return_value = bin_file

            flash_binary(base_dir, build_dir, "TEST", False)

            _find_connected_device.assert_called_once_with("TEST")
            _build_binary_file_path.assert_called_once_with(base_dir, build_dir, False)
            _flash_dev.assert_called_once_with(test_device.mount_points[0].resolve(), bin_file)


class TestBuildBinFilePath(TestCase):
    def test_build_bin_file_path(self):
        with tempfile.TemporaryDirectory() as tmpDir:
            base_dir = pathlib.Path(tmpDir)
            build_dir = base_dir / "cmake_build"
            build_dir.mkdir()
            bin_file = base_dir.name + ".bin"
            bin_file = build_dir / bin_file
            bin_file.touch()

            self.assertEqual(_build_binary_file_path(base_dir, build_dir, False), bin_file)

    def test_build_hex_file_path(self):
        with tempfile.TemporaryDirectory() as tmpDir:
            base_dir = pathlib.Path(tmpDir)
            build_dir = base_dir / "cmake_build"
            build_dir.mkdir()
            bin_file = base_dir.name + ".hex"
            bin_file = build_dir / bin_file
            bin_file.touch()

            self.assertEqual(_build_binary_file_path(base_dir, build_dir, True), bin_file)

    def test_missing_binary_file(self):
        with tempfile.TemporaryDirectory() as tmpDir:
            base_dir = pathlib.Path(tmpDir)
            build_dir = base_dir / "cmake_build"
            build_dir.mkdir()

            with self.assertRaises(BinaryFileNotFoundError):
                _build_binary_file_path(base_dir, build_dir, False)


@mock.patch("mbed_tools.build.flash.get_connected_devices")
class TestFindConnectedDevices(TestCase):
    def test_check_missing_device(self, get_connected_devices):
        get_connected_devices.return_value = ConnectedDevicesFactory()
        with self.assertRaises(DeviceNotFoundError):
            _find_connected_device("TEST")

    def test_connected_device(self, get_connected_devices):
        test_device = DeviceFactory()

        test_connected_devices = ConnectedDevices()
        test_connected_devices.identified_devices = [test_device]
        get_connected_devices.return_value = test_connected_devices

        self.assertEqual(_find_connected_device("TEST"), test_device)


@mock.patch("mbed_tools.build.flash.shutil.copy")
class TestCopyToDevice(TestCase):
    def test_copy_to_device(self, copy):
        test_device = DeviceFactory()

        with tempfile.TemporaryDirectory() as tmpDir:
            base_dir = pathlib.Path(tmpDir)
            build_dir = base_dir / "cmake_build"
            build_dir.mkdir()
            bin_file = base_dir.name + ".bin"
            bin_file = build_dir / bin_file
            bin_file.touch()
            _flash_dev(test_device.mount_points[0].resolve(), bin_file)

            copy.assert_called_once_with(bin_file, test_device.mount_points[0].resolve(), follow_symlinks=False)
