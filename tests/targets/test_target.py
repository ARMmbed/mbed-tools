#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib
import tempfile

from unittest import TestCase
from mbed_tools.targets.target import Target
from mbed_tools.targets.exceptions import TargetError


class TestTarget(TestCase):
    def test_get_target(self):
        contents = """{
            "Target": {
                "attribute_1": "Hello",
                "features": ["element_1"]
            },
            "Target_2": {
                "inherits": ["Target"],
                "config": {"Greeting": "Hello indeed!"},
                "features_add": ["element_2", "element_3"]
            },
            "Target_3": {
                "inherits": ["Target_2"],
                "features_remove": ["element_2"]
            }
        }"""
        with tempfile.TemporaryDirectory() as directory:
            targets_json_path = pathlib.Path(directory, "targets.json")
            targets_json_path.touch()
            targets_json_path.write_text(contents)
            target_name = "Target_3"
            result = Target.from_targets_json(target_name, targets_json_path)

        self.assertEqual(result.features, frozenset(["element_1", "element_3"]))
        self.assertEqual(result.config, {"Greeting": "Hello indeed!"})

    def test_get_target_not_found_in_targets_json(self):
        contents = """{
            "Target": {
                "attribute_1": "Hello",
                "device_has": ["element_1"]
            },
            "Target_2": {
                "inherits": ["Target"],
                "attribute_1": "Hello indeed!",
                "device_has_add": ["element_2", "element_3"]
            },
            "Target_3": {
                "inherits": ["Target_2"],
                "device_has_remove": ["element_2"]
            }
        }"""
        with tempfile.TemporaryDirectory() as directory:
            targets_json_path = pathlib.Path(directory, "targets.json")
            targets_json_path.write_text(contents)
            target_name = "Im_not_in_targets_json"
            with self.assertRaises(TargetError) as context:
                Target.from_targets_json(target_name, targets_json_path)
            self.assertEqual(str(context.exception), f"Target attributes for {target_name} not found.")

    def test_get_target_bad_path(self):
        path = pathlib.Path("i", "am", "bad")
        target_name = "Target_3"
        with self.assertRaises(TargetError) as context:
            Target.from_targets_json(target_name, path)
        self.assertIn("No such file or directory:", str(context.exception))
