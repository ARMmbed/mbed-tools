#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib
import tempfile
from unittest import TestCase, mock
from mbed_tools.targets.exceptions import UnknownBoard

from tests.devices.factories import CandidateDeviceFactory
from mbed_tools.devices._internal.htm_file import OnlineId
from mbed_tools.devices._internal.resolve_board import (
    NoBoardForCandidate,
    resolve_board,
    _get_all_htm_files_contents,
    _read_htm_file_contents,
    _is_htm_file,
)


@mock.patch(
    "mbed_tools.devices._internal.resolve_board._get_all_htm_files_contents",
    autospec=True,
    return_value=["some file contents"],
)
@mock.patch("mbed_tools.devices._internal.resolve_board.read_product_code", autospec=True)
@mock.patch("mbed_tools.devices._internal.resolve_board.get_board_by_product_code", autospec=True)
class TestResolveBoardUsingProductCodeFromHTM(TestCase):
    def test_returns_resolved_target(self, get_board_by_product_code, read_product_code, _get_all_htm_files_contents):
        read_product_code.return_value = "0123"
        candidate = CandidateDeviceFactory()

        subject = resolve_board(candidate)

        self.assertEqual(subject, get_board_by_product_code.return_value)
        get_board_by_product_code.assert_called_once_with(read_product_code.return_value)
        read_product_code.assert_called_once_with(_get_all_htm_files_contents.return_value[0])
        _get_all_htm_files_contents.assert_called_once_with(candidate.mount_points)

    def test_raises_when_board_not_found(
        self, get_board_by_product_code, read_product_code, _get_all_htm_files_contents
    ):
        read_product_code.return_value = "1234"
        get_board_by_product_code.side_effect = UnknownBoard
        candidate = CandidateDeviceFactory()

        with self.assertRaises(NoBoardForCandidate):
            resolve_board(candidate)


@mock.patch(
    "mbed_tools.devices._internal.resolve_board._get_all_htm_files_contents",
    autospec=True,
    return_value=["other file contents"],
)
@mock.patch("mbed_tools.devices._internal.resolve_board.read_product_code", autospec=True, return_value=None)
@mock.patch("mbed_tools.devices._internal.resolve_board.read_online_id", autospec=True)
@mock.patch("mbed_tools.devices._internal.resolve_board.get_board_by_online_id", autospec=True)
class TestResolveBoardUsingOnlineIdFromHTM(TestCase):
    def test_returns_resolved_board(
        self, get_board_by_online_id, read_online_id, read_product_code, _get_all_htm_files_contents
    ):
        online_id = OnlineId(target_type="hat", slug="boat")
        read_online_id.return_value = online_id
        candidate = CandidateDeviceFactory()

        subject = resolve_board(candidate)

        self.assertEqual(subject, get_board_by_online_id.return_value)
        read_online_id.assert_called_with(_get_all_htm_files_contents.return_value[0])
        get_board_by_online_id.assert_called_once_with(target_type=online_id.target_type, slug=online_id.slug)

    def test_raises_when_board_not_found(
        self, get_board_by_online_id, read_online_id, read_product_code, _get_all_htm_files_contents
    ):
        read_online_id.return_value = OnlineId(target_type="hat", slug="boat")
        get_board_by_online_id.side_effect = UnknownBoard
        candidate = CandidateDeviceFactory()

        with self.assertRaises(NoBoardForCandidate):
            resolve_board(candidate)


@mock.patch(
    "mbed_tools.devices._internal.resolve_board._get_all_htm_files_contents",
    autospec=True,
    return_value=["who knows file contents"],
)
@mock.patch("mbed_tools.devices._internal.resolve_board.read_product_code", autospec=True, return_value=None)
@mock.patch("mbed_tools.devices._internal.resolve_board.read_online_id", autospec=True, return_value=None)
@mock.patch("mbed_tools.devices._internal.resolve_board.get_board_by_product_code", autospec=True)
class TestResolveBoardUsingProductCodeFromSerial(TestCase):
    def test_resolves_board_using_product_code_when_available(
        self, get_board_by_product_code, read_online_id, read_product_code, _get_all_htm_files_contents
    ):
        candidate = CandidateDeviceFactory()

        subject = resolve_board(candidate)

        self.assertEqual(subject, get_board_by_product_code.return_value)
        get_board_by_product_code.assert_called_once_with(candidate.serial_number[:4])

    def test_raises_when_board_not_found(
        self, get_board_by_product_code, read_online_id, read_product_code, _get_all_htm_files_contents
    ):
        get_board_by_product_code.side_effect = UnknownBoard
        candidate = CandidateDeviceFactory()

        with self.assertRaises(NoBoardForCandidate):
            resolve_board(candidate)


class TestGetAllHtmFilesContents(TestCase):
    def test_returns_contents_of_all_htm_files_in_given_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_1 = pathlib.Path(directory, "test-1")
            directory_1.mkdir()
            directory_2 = pathlib.Path(directory, "test-2")
            directory_2.mkdir()
            pathlib.Path(directory_1, "mbed.htm").write_text("foo")
            pathlib.Path(directory_2, "whatever.htm").write_text("bar")
            pathlib.Path(directory_1, "file.txt").write_text("txt files should not be read")
            pathlib.Path(directory_1, "._MBED.HTM").write_text("hidden files should not be read")

            result = _get_all_htm_files_contents([directory_1, directory_2])

        self.assertEqual(result, ["foo", "bar"])


class TestReadHtmFilesContents(TestCase):
    def test_handles_unreadable_htm_file(self):
        with tempfile.TemporaryDirectory() as directory:
            htm_file = pathlib.Path(directory, "mbed.htm")
            htm_file.write_text("foo")

            result = _read_htm_file_contents([htm_file, pathlib.Path("error.htm")])

        self.assertEqual(result, ["foo"])


class TestIsHtmFile(TestCase):
    def test_lower_case_htm(self):
        result = _is_htm_file(pathlib.Path("mbed.htm"))
        self.assertEqual(True, result)

    def test_upper_case_htm(self):
        result = _is_htm_file(pathlib.Path("MBED.HTM"))
        self.assertEqual(True, result)

    def test_hidden_htm(self):
        result = _is_htm_file(pathlib.Path(".htm"))
        self.assertEqual(False, result)

    def test_text_file(self):
        result = _is_htm_file(pathlib.Path("mbed.txt"))
        self.assertEqual(False, result)
