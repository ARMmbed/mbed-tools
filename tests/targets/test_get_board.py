#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tests for `mbed_tools.targets.get_board`."""
from unittest import mock, TestCase

# Import from top level as this is the expected interface for users
from mbed_tools.targets import get_board_by_online_id, get_board_by_product_code
from mbed_tools.targets.get_board import (
    _DatabaseMode,
    _get_database_mode,
    get_board,
)
from mbed_tools.targets.env import env
from mbed_tools.targets.exceptions import UnknownBoard, UnsupportedMode
from tests.targets.factories import make_board


@mock.patch("mbed_tools.targets.get_board.Boards", autospec=True)
@mock.patch("mbed_tools.targets.get_board.env", spec_set=env)
class TestGetBoard(TestCase):
    def test_online_mode(self, env, mocked_boards):
        env.MBED_DATABASE_MODE = "ONLINE"
        fn = mock.Mock()

        subject = get_board(fn)

        self.assertEqual(subject, mocked_boards.from_online_database().get_board.return_value)
        mocked_boards.from_online_database().get_board.assert_called_once_with(fn)

    def test_offline_mode(self, env, mocked_boards):
        env.MBED_DATABASE_MODE = "OFFLINE"
        fn = mock.Mock()

        subject = get_board(fn)

        self.assertEqual(subject, mocked_boards.from_offline_database().get_board.return_value)
        mocked_boards.from_offline_database().get_board.assert_called_once_with(fn)

    def test_auto_mode_calls_offline_boards_first(self, env, mocked_boards):
        env.MBED_DATABASE_MODE = "AUTO"
        fn = mock.Mock()

        subject = get_board(fn)

        self.assertEqual(subject, mocked_boards.from_offline_database().get_board.return_value)
        mocked_boards.from_online_database().get_board.assert_not_called()
        mocked_boards.from_offline_database().get_board.assert_called_once_with(fn)

    def test_auto_mode_falls_back_to_online_database_when_board_not_found(self, env, mocked_boards):
        env.MBED_DATABASE_MODE = "AUTO"
        mocked_boards.from_offline_database().get_board.side_effect = UnknownBoard
        fn = mock.Mock()

        subject = get_board(fn)

        self.assertEqual(subject, mocked_boards.from_online_database().get_board.return_value)
        mocked_boards.from_offline_database().get_board.assert_called_once_with(fn)
        mocked_boards.from_online_database().get_board.assert_called_once_with(fn)


class TestGetBoardByProductCode(TestCase):
    @mock.patch("mbed_tools.targets.get_board.get_board")
    def test_matches_boards_by_product_code(self, mock_get_board):
        product_code = "swag"

        self.assertEqual(get_board_by_product_code(product_code), mock_get_board.return_value)

        # Test callable matches correct boards
        fn = mock_get_board.call_args[0][0]

        matching_board = make_board(product_code=product_code)
        not_matching_board = make_board(product_code="whatever")

        self.assertTrue(fn(matching_board))
        self.assertFalse(fn(not_matching_board))


class TestGetBoardByOnlineId(TestCase):
    @mock.patch("mbed_tools.targets.get_board.get_board")
    def test_matches_boards_by_online_id(self, mock_get_board):
        target_type = "platform"

        self.assertEqual(get_board_by_online_id(slug="slug", target_type=target_type), mock_get_board.return_value)

        # Test callable matches correct boards
        fn = mock_get_board.call_args[0][0]

        matching_board_1 = make_board(target_type=target_type, slug="slug")
        matching_board_2 = make_board(target_type=target_type, slug="SlUg")
        not_matching_board = make_board(target_type=target_type, slug="whatever")

        self.assertTrue(fn(matching_board_1))
        self.assertTrue(fn(matching_board_2))
        self.assertFalse(fn(not_matching_board))


@mock.patch("mbed_tools.targets.get_board.env", spec_set=env)
class TestGetDatabaseMode(TestCase):
    def test_returns_configured_database_mode(self, env):
        env.MBED_DATABASE_MODE = "OFFLINE"
        self.assertEqual(_get_database_mode(), _DatabaseMode.OFFLINE)

    def test_raises_when_configuration_is_not_supported(self, env):
        env.MBED_DATABASE_MODE = "NOT_VALID"
        with self.assertRaises(UnsupportedMode):
            _get_database_mode()
