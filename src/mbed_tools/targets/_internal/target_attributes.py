#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Internal helper to retrieve target attribute information.

This information is parsed from the targets.json configuration file
found in the mbed-os repo.
"""
import json
import pathlib
from json.decoder import JSONDecodeError
from typing import Dict, Any, Set, Optional, cast

from mbed_tools.lib.exceptions import ToolsError

from mbed_tools.targets._internal.targets_json_parsers.accumulating_attribute_parser import (
    get_accumulating_attributes_for_target,
)
from mbed_tools.targets._internal.targets_json_parsers.overriding_attribute_parser import (
    get_overriding_attributes_for_target,
    get_labels_for_target,
)
from mbed_tools.targets._internal.exceptions import TargetsJsonConfigurationError

INTERNAL_PACKAGE_DIR = pathlib.Path(__file__).parent
MBED_OS_METADATA_FILE = pathlib.Path(INTERNAL_PACKAGE_DIR, "data", "targets_metadata.json")


class TargetAttributesError(ToolsError):
    """Target attributes error."""


class ParsingTargetsJSONError(TargetAttributesError):
    """targets.json parsing failed."""


class TargetNotFoundError(TargetAttributesError):
    """Target definition not found in targets.json."""


def get_target_attributes(path_to_targets_json: pathlib.Path, target_name: str) -> dict:
    """Retrieves attribute data taken from targets.json for a single target.

    Args:
        path_to_targets_json: an absolute or relative path to the location of targets.json.
        target_name: the name of the target (often a Board's board_type).

    Returns:
        A dictionary representation of the attributes for the target.

    Raises:
        FileNotFoundError: path provided does not lead to targets.json
        ParsingTargetJSONError: error parsing targets.json
        TargetNotFoundError: there is no target attribute data found for that target.
    """
    targets_json_path = path_to_targets_json
    all_targets_data = _read_json_file(targets_json_path)
    target_attributes = _extract_target_attributes(all_targets_data, target_name)
    target_attributes["labels"] = get_labels_for_target(all_targets_data, target_name).union(
        _extract_core_labels(target_attributes.get("core", None))
    )
    target_attributes["extra_labels"] = set(target_attributes.get("extra_labels", []))
    target_attributes["features"] = set(target_attributes.get("features", []))
    target_attributes["components"] = set(target_attributes.get("components", []))
    target_attributes["macros"] = set(target_attributes.get("macros", []))
    target_attributes["config"] = _apply_config_overrides(
        target_attributes.get("config", {}), target_attributes.get("overrides", {})
    )
    return target_attributes


def _read_json_file(path_to_file: pathlib.Path) -> dict:
    """Reads the data from a json file.

    Args:
        path_to_file: location of the json file.

    Returns:
        A dictionary representation of all the data in the json file.

    Raises:
        ParsingTargetJSONError: error parsing targets.json
        FileNotFoundError: path provided does not lead to a valid json file
    """
    try:
        # mypy doesn't recognise that json.loads always returns a dictionary
        return cast(dict, json.loads(path_to_file.read_text()))
    except JSONDecodeError as json_err:
        raise ParsingTargetsJSONError(f"Invalid JSON found in '{path_to_file}'.") from json_err


def _extract_target_attributes(all_targets_data: Dict[str, Any], target_name: str) -> dict:
    """Extracts the definition for a particular target from all the targets in targets.json.

    Args:
        all_targets_data: a dictionary representation of the raw targets.json data.
        target_name: the name of the target.

    Returns:
        A dictionary representation the target definition.

    Raises:
        TargetNotFoundError: no target definition found in targets.json.
    """
    if target_name not in all_targets_data:
        raise TargetNotFoundError(f"Target attributes for {target_name} not found.")

    # All target definitions are assumed to be public unless specifically set as public=false
    if not all_targets_data[target_name].get("public", True):
        raise TargetNotFoundError(f"Target attributes for {target_name} not found.")

    target_attributes = get_overriding_attributes_for_target(all_targets_data, target_name)
    accumulated_attributes = get_accumulating_attributes_for_target(all_targets_data, target_name)
    target_attributes.update(accumulated_attributes)
    return target_attributes


def _extract_core_labels(target_core: Optional[str]) -> Set[str]:
    """Find the labels associated with the target's core.

    Args:
        target_core: the target core, set as a build attribute

    Returns:
        A list of labels associated with the target's core, or an empty set
        if either core is undefined or no labels found for the core.
    """
    if target_core:
        mbed_os_metadata = _read_json_file(MBED_OS_METADATA_FILE)
        return set(mbed_os_metadata["CORE_LABELS"].get(target_core, []))
    return set()


def _apply_config_overrides(config: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Returns the config attribute with any overrides applied.

    Args:
        config: the cumulative config settings defined for a target
        overrides: the values that need to be changed in the config settings for this target

    Returns:
        The config settings with the overrides applied.

    Raises:
        TargetsJsonConfigurationError: overrides can't be applied to config settings that aren't already defined
    """
    config = config.copy()
    for key in overrides:
        try:
            config[key]["value"] = overrides[key]
        except KeyError:
            raise TargetsJsonConfigurationError("Cannot override config setting that is not defined.")
    return config
