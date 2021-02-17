#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pytest

from mbed_tools.lib.python_helpers import minimum_python_version, named_tuple_with_defaults, flatten_nested


class TestPythonHelpers:
    def test_python_version(self):
        # Tools only support Python>= 3.6
        assert minimum_python_version(3, 6)
        # With a bit of luck, python 100.100 is not coming tomorrow
        assert not minimum_python_version(100, 100)

    def test_named_tuple_with_defaults(self):
        named_tuple = named_tuple_with_defaults("TestNamedTuple", field_names=["field1", "field2"], defaults=[1, 2])
        a_tuple = named_tuple()
        assert a_tuple
        assert a_tuple.field1 == 1
        assert a_tuple.field2 == 2

        a_tuple = named_tuple(field1=15)
        assert a_tuple.field1 == 15
        assert a_tuple.field2 == 2


@pytest.mark.parametrize(
    "input_list, expected_result",
    (
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        ([1, [2], 3, 4, 5], [1, 2, 3, 4, 5]),
        ([[1, 2, 3], [4, 5]], [1, 2, 3, 4, 5]),
        ([(1, 2, 3), (4, 5)], [1, 2, 3, 4, 5]),
        ([[1, [[2, [3]]]], [4, 5]], [1, 2, 3, 4, 5]),
        ([["alan", [["bob", ["sally"]]]], ["jim", "jenny"]], ["alan", "bob", "sally", "jim", "jenny"]),
    ),
)
def test_flatten_nested_list(input_list, expected_result):
    assert flatten_nested(input_list) == expected_result
