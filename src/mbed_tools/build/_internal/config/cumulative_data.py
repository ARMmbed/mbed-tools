#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Ability to parse cumulative attributes from Sources."""
import itertools
import re
from dataclasses import dataclass, field, fields
from typing import Any, Iterable, Set, Tuple

from mbed_tools.build._internal.config.source import Source


@dataclass
class CumulativeData:
    """Representation of cumulative attributes assembled during Source parsing."""

    features: Set[str] = field(default_factory=set)
    components: Set[str] = field(default_factory=set)
    labels: Set[str] = field(default_factory=set)
    extra_labels: Set[str] = field(default_factory=set)
    device_has: Set[str] = field(default_factory=set)
    macros: Set[str] = field(default_factory=set)

    @classmethod
    def from_sources(cls, sources: Iterable[Source]) -> "CumulativeData":
        """Interrogate each Source in turn to create final CumulativeData."""
        data = CumulativeData()
        for source in sources:
            for key, value in source.overrides.items():
                if key in CUMULATIVE_OVERRIDE_KEYS_IN_SOURCE:
                    _modify_field(data, key, value)
        return data


def _modify_field(data: CumulativeData, key: str, value: Any) -> None:
    """Mutates CumulativeData in place by adding, removing or resetting the value of a field."""
    key, modifier = _extract_target_modifier_data(key)
    if modifier == "add":
        new_value = getattr(data, key) | set(value)
    elif modifier == "remove":
        new_value = getattr(data, key) - set(value)
    else:
        new_value = set(value)
    setattr(data, key, new_value)


_CUMULATIVE_FIELDS = [f.name for f in fields(CumulativeData)]
_PREFIXED_CUMULATIVE_FIELDS = [f"target.{f}" for f in _CUMULATIVE_FIELDS]
CUMULATIVE_OVERRIDE_KEYS_IN_SOURCE = _PREFIXED_CUMULATIVE_FIELDS + [
    f"{attr}_{suffix}" for attr, suffix in itertools.product(_PREFIXED_CUMULATIVE_FIELDS, ["add", "remove"])
]


def _extract_target_modifier_data(key: str) -> Tuple[str, str]:
    regex = fr"""
            (?P<key>{'|'.join(_CUMULATIVE_FIELDS)}) # attribute name (one of ACCUMULATING_OVERRIDES)
            _?                                      # separator
            (?P<modifier>(add|remove)?)             # modifier (add, remove or empty)
    """
    match = re.search(regex, key, re.VERBOSE)
    if not match:
        raise ValueError(f"Not a target modifier key {key}")
    return match["key"], match["modifier"]
