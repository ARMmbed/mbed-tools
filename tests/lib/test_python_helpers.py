#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import unittest

from mbed_tools.lib.python_helpers import minimum_python_version, named_tuple_with_defaults


class TestPythonHelpers(unittest.TestCase):
    def test_python_version(self):
        # Tools only support Python>= 3.6
        self.assertTrue(minimum_python_version(3, 6))
        # With a bit of luck, python 100.100 is not coming tomorrow
        self.assertFalse(minimum_python_version(100, 100))

    def test_named_tuple_with_defaults(self):
        named_tuple = named_tuple_with_defaults("TestNamedTuple", field_names=["field1", "field2"], defaults=[1, 2])
        a_tuple = named_tuple()
        self.assertIsNotNone(a_tuple)
        self.assertEqual(a_tuple.field1, 1)
        self.assertEqual(a_tuple.field2, 2)

        a_tuple = named_tuple(field1=15)
        self.assertEqual(a_tuple.field1, 15)
        self.assertEqual(a_tuple.field2, 2)
