#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

from mbed_tools.targets.mbed_tools import env_variables


class TestEnvVariables(TestCase):
    def test_expected_env_variables_are_exposed(self):
        exposed = set(variable.name for variable in env_variables)
        expected = {"MBED_DATABASE_MODE", "MBED_API_AUTH_TOKEN"}
        self.assertEqual(exposed, expected)
