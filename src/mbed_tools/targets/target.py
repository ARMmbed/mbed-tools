#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Representation of a Target."""
import pathlib

from dataclasses import dataclass
from typing import FrozenSet, Dict, Optional

from mbed_tools.targets.exceptions import TargetError
from mbed_tools.targets._internal import target_attributes


@dataclass(frozen=True, order=True)
class Target:
    """Representation of a Target as defined in Mbed OS library's targets.json file.

    Target contains properties that define how to build Mbed applications.

    Attributes:
        labels: Sections of Mbed OS code to be included in builds for this target.
        features: Sections of Mbed OS feature code to be included in builds for this target.
        components: Sections of Mbed OS component code to be included in builds for this target.
        config: Build configuration defaults for this target.
        supported_toolchains: Toolchains that can be used to build for this target.
        default_toolchain: Default toolchain used to build for this target.
    """

    labels: FrozenSet[str]
    features: FrozenSet[str]
    components: FrozenSet[str]
    config: Dict[str, str]
    supported_toolchains: FrozenSet[str]
    supported_form_factors: FrozenSet[str]
    default_toolchain: Optional[str]
    core: str
    device_name: str
    printf_lib: str
    device_has: FrozenSet[str]
    macros: FrozenSet[str]

    @classmethod
    def from_targets_json(cls, name: str, path_to_targets_json: pathlib.Path) -> "Target":
        """Construct a Target with data from Mbed OS library's targets.json file.

        Args:
            name: the name of the target defined in targets.json
            path_to_targets_json: path to a valid targets.json file

        Raises:
            TargetError: an error has occurred while creating a Target
        """
        try:
            attributes = target_attributes.get_target_attributes(path_to_targets_json, name)
        except (FileNotFoundError, target_attributes.TargetAttributesError) as e:
            raise TargetError(e) from e

        return cls(
            labels=frozenset(attributes.get("labels", set()).union(attributes.get("extra_labels", set()))),
            features=frozenset(attributes.get("features", set())),
            components=frozenset(attributes.get("components", set())),
            config=attributes.get("config"),
            supported_toolchains=frozenset(attributes.get("supported_toolchains", [])),
            supported_form_factors=frozenset(attributes.get("supported_form_factors", [])),
            default_toolchain=attributes.get("default_toolchain", None),
            core=attributes.get("core", ""),
            device_name=attributes.get("device_name", ""),
            printf_lib=attributes.get("printf_lib", ""),
            device_has=frozenset(attributes.get("device_has", set())),
            macros=frozenset(attributes.get("macros", set())),
        )
