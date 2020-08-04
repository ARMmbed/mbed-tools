#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase, mock
from mbed_tools.targets.target import Target
from mbed_tools.targets.get_target import get_target_by_board_type, get_target_by_name


class TestGetTarget(TestCase):
    @mock.patch("mbed_tools.targets.get_target.Target", spec_set=Target)
    def test_get_by_name(self, MockTarget):
        target_name = "Target"
        targets_json_file_path = "targets.json"

        result = get_target_by_name(target_name, targets_json_file_path)

        self.assertEqual(result, MockTarget.from_targets_json.return_value)
        MockTarget.from_targets_json.assert_called_once_with(
            target_name, targets_json_file_path,
        )

    @mock.patch("mbed_tools.targets.get_target.get_target_by_name")
    def test_get_by_board_type(self, mock_get_target_by_name):
        board_type = "Board"
        path_to_mbed_program = "somewhere"

        result = get_target_by_board_type(board_type, path_to_mbed_program)

        self.assertEqual(result, mock_get_target_by_name.return_value)
        mock_get_target_by_name.assert_called_once_with(board_type, path_to_mbed_program)
