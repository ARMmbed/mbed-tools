#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import mock

import pytest

from mbed_tools.targets.exceptions import UnknownBoard

from tests.devices.factories import CandidateDeviceFactory
from mbed_tools.devices._internal.file_parser import OnlineId
from mbed_tools.devices._internal.resolve_board import (
    NoBoardForCandidate,
    resolve_board,
)


@mock.patch("mbed_tools.devices._internal.resolve_board.extract_product_code_from_htm", autospec=True)
@mock.patch("mbed_tools.devices._internal.resolve_board.get_board_by_product_code", autospec=True)
class TestResolveBoardUsingProductCodeFromHTM:
    def test_returns_resolved_target(self, get_board_by_product_code, extract_product_code_from_htm):
        extract_product_code_from_htm.return_value = "0123"
        candidate = CandidateDeviceFactory()

        subject = resolve_board(candidate)

        assert subject == get_board_by_product_code.return_value
        get_board_by_product_code.assert_called_once_with(extract_product_code_from_htm.return_value)

    def test_raises_when_board_not_found(self, get_board_by_product_code, extract_product_code_from_htm):
        extract_product_code_from_htm.return_value = "1234"
        get_board_by_product_code.side_effect = UnknownBoard
        candidate = CandidateDeviceFactory()

        with pytest.raises(NoBoardForCandidate):
            resolve_board(candidate)


@mock.patch(
    "mbed_tools.devices._internal.resolve_board.extract_product_code_from_htm", autospec=True, return_value=None
)
@mock.patch("mbed_tools.devices._internal.resolve_board.extract_online_id_from_htm", autospec=True)
@mock.patch("mbed_tools.devices._internal.resolve_board.get_board_by_online_id", autospec=True)
class TestResolveBoardUsingOnlineIdFromHTM:
    def test_returns_resolved_board(
        self, get_board_by_online_id, extract_online_id_from_htm, extract_product_code_from_htm,
    ):
        online_id = OnlineId(target_type="hat", slug="boat")
        extract_online_id_from_htm.return_value = online_id
        candidate = CandidateDeviceFactory()

        subject = resolve_board(candidate)

        assert subject == get_board_by_online_id.return_value
        get_board_by_online_id.assert_called_once_with(target_type=online_id.target_type, slug=online_id.slug)

    def test_raises_when_board_not_found(
        self, get_board_by_online_id, extract_online_id_from_htm, extract_product_code_from_htm,
    ):
        extract_online_id_from_htm.return_value = OnlineId(target_type="hat", slug="boat")
        get_board_by_online_id.side_effect = UnknownBoard
        candidate = CandidateDeviceFactory()

        with pytest.raises(NoBoardForCandidate):
            resolve_board(candidate)


@mock.patch(
    "mbed_tools.devices._internal.resolve_board.extract_product_code_from_htm", autospec=True, return_value=None
)
@mock.patch("mbed_tools.devices._internal.resolve_board.extract_online_id_from_htm", autospec=True, return_value=None)
@mock.patch("mbed_tools.devices._internal.resolve_board.get_board_by_product_code", autospec=True)
class TestResolveBoardUsingProductCodeFromSerial:
    def test_resolves_board_using_product_code_when_available(
        self, get_board_by_product_code, extract_online_id_from_htm, extract_product_code_from_htm,
    ):
        candidate = CandidateDeviceFactory()

        subject = resolve_board(candidate)

        assert subject == get_board_by_product_code.return_value
        get_board_by_product_code.assert_called_once_with(candidate.serial_number[:4])

    def test_raises_when_board_not_found(
        self, get_board_by_product_code, extract_online_id_from_htm, extract_product_code_from_htm,
    ):
        get_board_by_product_code.side_effect = UnknownBoard
        candidate = CandidateDeviceFactory()

        with pytest.raises(NoBoardForCandidate):
            resolve_board(candidate)
