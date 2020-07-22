#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Helpers for python language related functions."""
import sys
from collections import namedtuple
from typing import NamedTuple, Iterable, Any


def is_python_more_recent(major: int, minor: int) -> bool:
    """States whether the python in use is more recent than set major,minor versions."""
    return sys.version_info.major >= major and sys.version_info.minor >= minor


def named_tuple_with_defaults(typename: str, field_names: Iterable[str], defaults: Iterable[Any]) -> NamedTuple:
    """Gets a named tuple set with default values.

    defaults field only appeared in Python 3.7.
    See https://stackoverflow.com/questions/11351032/namedtuple-and-default-values-for-optional-keyword-arguments
    """
    if is_python_more_recent(3, 7):
        return namedtuple(typename=typename, field_names=field_names, defaults=defaults)  # type:ignore
    else:
        tuple: NamedTuple = namedtuple(typename=typename, field_names=field_names)  # type:ignore
        tuple.__new__.__defaults__ = (None,) * len(field_names)  # type:ignore
        return tuple  # type:ignore
