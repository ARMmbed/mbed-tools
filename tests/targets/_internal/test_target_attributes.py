#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tests for `mbed_tools.targets.target_attributes`."""
import pathlib
import tempfile
from unittest import TestCase, mock

from mbed_tools.targets._internal.exceptions import TargetsJsonConfigurationError
from mbed_tools.targets._internal.target_attributes import (
    ParsingTargetsJSONError,
    TargetNotFoundError,
    get_target_attributes,
    _read_json_file,
    _extract_target_attributes,
    _extract_core_labels,
    _apply_config_overrides,
)


class TestExtractTargetAttributes(TestCase):
    def test_no_target_found(self):
        all_targets_data = {
            "Target_1": "some attributes",
            "Target_2": "some more attributes",
        }
        with self.assertRaises(TargetNotFoundError):
            _extract_target_attributes(all_targets_data, "Unlisted_Target")

    def test_target_found(self):
        target_attributes = {"attribute1": "something"}

        all_targets_data = {
            "Target_1": target_attributes,
            "Target_2": "some more attributes",
        }
        # When not explicitly included public is assumed to be True
        self.assertEqual(_extract_target_attributes(all_targets_data, "Target_1"), target_attributes)

    def test_target_public(self):
        all_targets_data = {
            "Target_1": {"attribute1": "something", "public": True},
            "Target_2": "some more attributes",
        }
        # The public attribute affects visibility but is removed from result
        self.assertEqual(_extract_target_attributes(all_targets_data, "Target_1"), {"attribute1": "something"})

    def test_target_private(self):
        all_targets_data = {
            "Target_1": {"attribute1": "something", "public": False},
            "Target_2": "some more attributes",
        }
        with self.assertRaises(TargetNotFoundError):
            _extract_target_attributes(all_targets_data, "Target_1"),


class TestReadTargetsJSON(TestCase):
    def test_valid_path(self):
        contents = """{
            "Target_Name": {
                "attribute_1": []
            }
        }"""
        with tempfile.TemporaryDirectory() as directory:
            json_file = pathlib.Path(directory, "targets.json")
            json_file.write_text(contents)
            result = _read_json_file(json_file)

            self.assertEqual(type(result), dict)

    def test_invalid_path(self):
        json_file = pathlib.Path("i_dont_exist")

        with self.assertRaises(FileNotFoundError):
            _read_json_file(json_file)

    def test_malformed_json(self):
        contents = """{
            "Target_Name": {
                []
            }
        }"""
        with tempfile.TemporaryDirectory() as directory:
            json_file = pathlib.Path(directory, "targets.json")
            json_file.write_text(contents)

            with self.assertRaises(ParsingTargetsJSONError):
                _read_json_file(json_file)


class TestGetTargetAttributes(TestCase):
    @mock.patch("mbed_tools.targets._internal.target_attributes._read_json_file")
    @mock.patch("mbed_tools.targets._internal.target_attributes._extract_target_attributes")
    @mock.patch("mbed_tools.targets._internal.target_attributes.get_labels_for_target")
    @mock.patch("mbed_tools.targets._internal.target_attributes._extract_core_labels")
    def test_gets_attributes_for_target(
        self, extract_core_labels, get_labels_for_target, extract_target_attributes, read_json_file
    ):
        targets_json_path = pathlib.Path("mbed-os/targets/targets.json")
        target_name = "My_Target"
        build_attributes = {"attribute": "value"}
        extract_target_attributes.return_value = build_attributes

        result = get_target_attributes(targets_json_path, target_name)

        read_json_file.assert_called_once_with(targets_json_path)
        extract_target_attributes.assert_called_once_with(read_json_file.return_value, target_name)
        get_labels_for_target.assert_called_once_with(read_json_file.return_value, target_name)
        extract_core_labels.assert_called_once_with(build_attributes.get("core", None))
        self.assertEqual(result, extract_target_attributes.return_value)


class TestExtractCoreLabels(TestCase):
    @mock.patch("mbed_tools.targets._internal.target_attributes._read_json_file")
    def test_extract_core(self, read_json_file):
        core_labels = ["FOO", "BAR"]
        metadata = {"CORE_LABELS": {"core_name": core_labels}}
        read_json_file.return_value = metadata
        target_core = "core_name"

        result = _extract_core_labels(target_core)

        self.assertEqual(result, set(core_labels))

    def test_no_core(self):
        result = _extract_core_labels(None)
        self.assertEqual(result, set())

    @mock.patch("mbed_tools.targets._internal.target_attributes._read_json_file")
    def test_no_labels(self, read_json_file):
        metadata = {"CORE_LABELS": {"not_the_same_core": []}}
        read_json_file.return_value = metadata

        result = _extract_core_labels("core_name")

        self.assertEqual(result, set())


class TestApplyConfigOverrides(TestCase):
    def test_applies_overrides(self):
        config = {"foo": {"help": "Do a foo", "value": 0}}
        overrides = {"foo": 9}
        expected_result = {"foo": {"help": "Do a foo", "value": 9}}

        self.assertEqual(expected_result, _apply_config_overrides(config, overrides))

    def test_applies_no_overrides(self):
        config = {"foo": {"help": "Do a foo", "value": 0}}
        overrides = {}

        self.assertEqual(config, _apply_config_overrides(config, overrides))

    def test_overriding_non_existing_config(self):
        config = {"foo": {"help": "Do a foo", "value": 0}}
        overrides = {"bar": 9}
        with self.assertRaises(TargetsJsonConfigurationError):
            _apply_config_overrides(config, overrides)
