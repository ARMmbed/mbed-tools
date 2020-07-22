#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tests for `mbed_tools.targets._internal.board_database`."""

from unittest import TestCase, mock

import requests_mock

# Unit under test
import mbed_tools.targets._internal.board_database as board_database
from mbed_tools.targets.env import env


class TestGetOnlineBoardData(TestCase):
    """Tests for the method `board_database.get_online_board_data`."""

    @requests_mock.mock()
    @mock.patch("mbed_tools.targets._internal.board_database.logger.warning", autospec=True)
    @mock.patch("mbed_tools.targets._internal.board_database.logger.debug", autospec=True)
    def test_401(self, mock_request, logger_debug, logger_warning):
        """Given a 401 error code, BoardAPIError is raised."""
        mock_request.get(board_database._BOARD_API, status_code=401, text="Who are you?")
        with self.assertRaises(board_database.BoardAPIError):
            board_database.get_online_board_data()
        self.assertTrue("MBED_API_AUTH_TOKEN" in str(logger_warning.call_args), "Auth token should be mentioned")
        self.assertTrue("Who are you?" in str(logger_debug.call_args), "Message content should be in the debug message")

    @requests_mock.mock()
    @mock.patch("mbed_tools.targets._internal.board_database.logger.warning", autospec=True)
    @mock.patch("mbed_tools.targets._internal.board_database.logger.debug", autospec=True)
    def test_404(self, mock_request, logger_debug, logger_warning):
        """Given a 404 error code, TargetAPIError is raised."""
        mock_request.get(board_database._BOARD_API, status_code=404, text="Not Found")
        with self.assertRaises(board_database.BoardAPIError):
            board_database.get_online_board_data()
        self.assertTrue("404" in str(logger_warning.call_args), "HTTP status code should be mentioned")
        self.assertTrue("Not Found" in str(logger_debug.call_args), "Message content should be in the debug message")

    @requests_mock.mock()
    @mock.patch("mbed_tools.targets._internal.board_database.logger.warning", autospec=True)
    @mock.patch("mbed_tools.targets._internal.board_database.logger.debug", autospec=True)
    def test_200_invalid_json(self, mock_request, logger_debug, logger_warning):
        """Given a valid response but invalid json, JSONDecodeError is raised."""
        mock_request.get(board_database._BOARD_API, text="some text")
        with self.assertRaises(board_database.ResponseJSONError):
            board_database.get_online_board_data()
        self.assertTrue("Invalid JSON" in str(logger_warning.call_args), "Invalid JSON should be mentioned")
        self.assertTrue("some text" in str(logger_debug.call_args), "Message content should be in the debug message")

    @requests_mock.mock()
    @mock.patch("mbed_tools.targets._internal.board_database.logger.warning", autospec=True)
    @mock.patch("mbed_tools.targets._internal.board_database.logger.debug", autospec=True)
    def test_200_no_data_field(self, mock_request, logger_debug, logger_warning):
        """Given a valid response but no data field, ResponseJSONError is raised."""
        mock_request.get(board_database._BOARD_API, json={"notdata": [], "stillnotdata": {}})
        with self.assertRaises(board_database.ResponseJSONError):
            board_database.get_online_board_data()
        self.assertTrue("missing the 'data' field" in str(logger_warning.call_args), "Data field should be mentioned")
        self.assertTrue(
            "notdata, stillnotdata" in str(logger_debug.call_args),
            "JSON keys from message should be in the debug message",
        )

    @requests_mock.mock()
    def test_200_value_data(self, mock_request):
        """Given a valid response, target data is set from the returned json."""
        mock_request.get(board_database._BOARD_API, json={"data": 42})
        board_data = board_database.get_online_board_data()
        self.assertEqual(42, board_data, "Target data should match the contents of the target API data")

    @mock.patch("mbed_tools.targets._internal.board_database.requests")
    @mock.patch("mbed_tools.targets._internal.board_database.env", spec_set=env)
    def test_auth_header_set_with_token(self, env, requests):
        """Given an authorization token env variable, get is called with authorization header."""
        env.MBED_API_AUTH_TOKEN = "token"
        header = {"Authorization": "Bearer token"}
        board_database._get_request()
        requests.get.assert_called_once_with(board_database._BOARD_API, headers=header)

    @mock.patch("mbed_tools.targets._internal.board_database.requests")
    def test_no_auth_header_set_with_empty_token_var(self, requests):
        """Given no authorization token env variable, get is called with no header."""
        board_database._get_request()
        requests.get.assert_called_once_with(board_database._BOARD_API, headers=None)

    @mock.patch("mbed_tools.targets._internal.board_database.requests.get")
    def test_raises_tools_error_on_connection_error(self, get):
        get.side_effect = board_database.requests.exceptions.ConnectionError
        with self.assertRaises(board_database.BoardAPIError):
            board_database._get_request()


class TestGetOfflineTargetData(TestCase):
    """Tests for the method get_offline_target_data."""

    def test_local_target_database_file_found(self):
        """Test local database is found and loaded."""
        data = board_database.get_offline_board_data()
        self.assertTrue(len(data), "Some data should be returned from local database file.")

    @mock.patch("mbed_tools.targets._internal.board_database.get_board_database_path")
    def test_raises_on_invalid_json(self, mocked_get_file):
        """Test raises an error when the file contains invalid JSON."""
        invalid_json = "None"
        path_mock = mock.Mock()
        path_mock.read_text.return_value = invalid_json
        mocked_get_file.return_value = path_mock
        with self.assertRaises(board_database.ResponseJSONError):
            board_database.get_offline_board_data()


class TestGetLocalTargetDatabaseFile(TestCase):
    def test_returns_path_to_targets(self):
        path = board_database.get_board_database_path()
        self.assertEqual(path.exists(), True, "Path to boards should exist in the package data folder.")
