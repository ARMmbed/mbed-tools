#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase
from mbed_tools.targets.mbed_tools import env_variables as targets_env_variables

from mbed_tools.devices.mbed_tools import cli, env_variables
from mbed_tools.devices._internal.mbed_tools.list_connected_devices import list_connected_devices


class TestCli(TestCase):
    def test_aliases_list_connected_devices(self):
        self.assertEqual(cli, list_connected_devices)


class TestEnvVariables(TestCase):
    def test_aliases_list_of_env_variables_from_targets(self):
        self.assertEqual(env_variables, targets_env_variables)
