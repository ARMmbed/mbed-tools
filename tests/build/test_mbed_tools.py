#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

from mbed_tools.build._internal.mbed_tools.configure import configure
from mbed_tools.build import mbed_tools


class TestExport(TestCase):
    def test_aliases_export(self):
        self.assertEqual(mbed_tools.configure, configure)
