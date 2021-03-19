#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import mock

import pytest

from mbed_tools.targets.exceptions import UnknownBoard

from mbed_tools.devices._internal.file_parser import OnlineId, DeviceFileInfo
from mbed_tools.devices._internal.resolve_board import (
    NoBoardForCandidate,
    resolve_board,
)


@pytest.fixture
def get_board_by_product_code_mock():
    with mock.patch("mbed_tools.devices._internal.resolve_board.get_board_by_product_code", autospec=True) as gbp:
        yield gbp


@pytest.fixture
def get_board_by_online_id_mock():
    with mock.patch("mbed_tools.devices._internal.resolve_board.get_board_by_online_id", autospec=True) as gbp:
        yield gbp


class TestResolveBoardUsingProductCodeFromHTM:
    def test_returns_resolved_target(self, get_board_by_product_code_mock):
        dev_info = DeviceFileInfo("0123", None)

        subject = resolve_board(product_code=dev_info.product_code)

        assert subject == get_board_by_product_code_mock.return_value
        get_board_by_product_code_mock.assert_called_once_with(dev_info.product_code)

    def test_raises_when_board_not_found(self, get_board_by_product_code_mock):
        get_board_by_product_code_mock.side_effect = UnknownBoard

        with pytest.raises(NoBoardForCandidate):
            resolve_board(product_code="0123")


class TestResolveBoardUsingOnlineIdFromHTM:
    def test_returns_resolved_board(self, get_board_by_online_id_mock):
        online_id = OnlineId(target_type="hat", slug="boat")

        subject = resolve_board(online_id=online_id)

        assert subject == get_board_by_online_id_mock.return_value
        get_board_by_online_id_mock.assert_called_once_with(target_type=online_id.target_type, slug=online_id.slug)

    def test_raises_when_board_not_found(self, get_board_by_online_id_mock):
        get_board_by_online_id_mock.side_effect = UnknownBoard

        with pytest.raises(NoBoardForCandidate):
            resolve_board(online_id=OnlineId(target_type="hat", slug="boat"))


class TestResolveBoardUsingProductCodeFromSerial:
    def test_resolves_board_using_product_code_when_available(self, get_board_by_product_code_mock):
        serial_number = "0A9KJFKD0993WJKUFS0KLJ329090"
        subject = resolve_board(serial_number=serial_number)

        assert subject == get_board_by_product_code_mock.return_value
        get_board_by_product_code_mock.assert_called_once_with(serial_number[:4])

    def test_raises_when_board_not_found(self, get_board_by_product_code_mock):
        get_board_by_product_code_mock.side_effect = UnknownBoard

        with pytest.raises(NoBoardForCandidate):
            resolve_board(serial_number="0")
