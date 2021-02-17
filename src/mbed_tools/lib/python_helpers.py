#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Helpers for python language related functions."""
import sys
from collections import namedtuple
from typing import NamedTuple, Iterable, Any, List, cast


def minimum_python_version(major: int, minor: int) -> bool:
    """States whether the python in use is more recent than set major,minor versions."""
    return sys.version_info.major >= major and sys.version_info.minor >= minor


def named_tuple_with_defaults(typename: str, field_names: Iterable[str], defaults: Iterable[Any]) -> NamedTuple:
    """Gets a named tuple set with default values.

    defaults field only appeared in Python 3.7.
    See https://stackoverflow.com/questions/11351032/namedtuple-and-default-values-for-optional-keyword-arguments
    """
    if minimum_python_version(3, 7):
        return namedtuple(typename=typename, field_names=field_names, defaults=defaults)  # type: ignore
    else:
        a_tuple: NamedTuple = namedtuple(typename=typename, field_names=field_names)  # type: ignore
        a_tuple.__new__.__defaults__ = tuple(defaults)  # type: ignore
        return cast(NamedTuple, a_tuple)


def flatten_nested(input_iter: Iterable) -> List:
    """Flatten a nested Iterable with arbitrary levels of nesting.

    If the input is an iterator then this function will exhaust it.

    Args:
        input_iter: The input Iterable which may or may not be nested.

    Returns:
        A flat list created from the input_iter.
        If input_iter has no nesting its elements are appended to a list and returned.
    """
    output = []
    for elem in input_iter:
        if isinstance(elem, Iterable) and not isinstance(elem, str):
            output += flatten_nested(elem)
        else:
            output.append(elem)

    return output
