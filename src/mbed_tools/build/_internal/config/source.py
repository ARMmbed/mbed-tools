#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Configuration source abstraction."""
import json
import logging

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Any

logger = logging.getLogger(__name__)


@dataclass
class Source:
    """Configuration source abstraction.

    MbedOS build configuration is assembled from various sources:
    - targets.json
    - mbed_lib.json
    - mbed_app.json

    This class provides a common interface to configuration data.
    """

    human_name: str
    config: dict
    overrides: dict
    macros: Iterable[str]

    @classmethod
    def from_mbed_lib(cls, mbed_lib_path: Path, target_labels: Iterable[str]) -> "Source":
        """Build Source from mbed_lib.json file.

        Args:
            mbed_lib_path: Path to mbed_lib.json file
            target_labels: Labels for which "target_overrides" should apply
        """
        file_contents = _decode_json_file(mbed_lib_path)
        namespace = file_contents["name"]

        return cls.from_file_contents(
            file_name=str(mbed_lib_path), file_contents=file_contents, namespace=namespace, target_labels=target_labels
        )

    @classmethod
    def from_mbed_app(cls, mbed_app_path: Path, target_labels: Iterable[str]) -> "Source":
        """Build Source from mbed_app.json file.

        Args:
            mbed_app_path: Path to mbed_app.json file
            target_labels: Labels for which "target_overrides" should apply
        """
        file_contents = _decode_json_file(mbed_app_path)
        return cls.from_file_contents(
            file_name=str(mbed_app_path), file_contents=file_contents, namespace="app", target_labels=target_labels
        )

    @classmethod
    def from_file_contents(
        cls, file_name: str, file_contents: dict, namespace: str, target_labels: Iterable[str]
    ) -> "Source":
        """Build Source from file contents."""
        config = file_contents.get("config", {})
        config = _namespace_data(config, namespace)

        overrides = file_contents.get("target_overrides", {})
        target_specific_overrides = _filter_target_overrides(overrides, target_labels)
        namespaced_overrides = _namespace_data(target_specific_overrides, namespace)

        macros = file_contents.get("macros", [])

        return cls(human_name=f"File: {file_name}", config=config, overrides=namespaced_overrides, macros=macros)

    @classmethod
    def from_target(cls, target: dict) -> "Source":
        """Build Source from retrieved mbed_tools.targets.Target data."""
        namespace = "target"
        config = _namespace_data(target["config"], namespace)

        overrides = {
            "features": target["features"],
            "components": target["components"],
            "labels": target["labels"],
            "extra_labels": target["extra_labels"],
            "macros": target["macros"],
        }
        namespaced_overrides = _namespace_data(overrides, namespace)

        return cls(
            human_name=f"mbed_target.Target for {target}", config=config, overrides=namespaced_overrides, macros=[],
        )


def _filter_target_overrides(data: dict, allowed_labels: Iterable[str]) -> dict:
    """Flatten and filter target overrides.

    Ensures returned dictionary only contains configuration settings applicable to given allowed labels.
    """
    flattened = {}
    for target_label, overrides in data.items():
        if target_label == "*" or target_label in allowed_labels:
            flattened.update(overrides)
    return flattened


def _namespace_data(data: dict, namespace: str) -> dict:
    """Prefix configuration key with a namespace.

    Namespace is ConfigSource wide, and is resolved at source build time.

    It should be one of:
    - "target"
    - "app"
    - library name (where "mbed_lib.json" comes from)

    If given key is already namespaced, return it as is - this is going to be the case for
    keys from "target_overrides" entries. Keys from "config" usually need namespacing.
    """
    namespaced = {}
    for key, value in data.items():
        if "." not in key:
            key = f"{namespace}.{key}"
        namespaced[key] = value
    return namespaced


def _decode_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON data in the file located at '{path}'")
        raise
