#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import pathlib
import tempfile
from unittest import TestCase

from mbed_tools.build._internal.config.source import (
    Source,
    _namespace_data,
    _filter_target_overrides,
    _decode_json_file,
)


class TestSource(TestCase):
    def test_from_mbed_lib(self):
        with tempfile.TemporaryDirectory() as directory:
            data = {
                "name": "foo",
                "config": {"a-number": 123, "a-bool": {"help": "Simply a boolean", "value": True}},
                "target_overrides": {
                    "*": {"a-number": 456, "target.features_add": ["FOO"]},
                    "NOT_THIS_TARGET": {"a-string": "foo", "target.features_add": ["BAR"]},
                    "THIS_TARGET": {"a-bool": False, "other-lib.something-else": "blah"},
                },
                "macros": ["MACRO=1"],
            }
            file = pathlib.Path(directory, "mbed_lib.json")
            file.write_text(json.dumps(data))

            subject = Source.from_mbed_lib(file, ["THIS_TARGET"])

        self.assertEqual(
            subject,
            Source(
                human_name=f"File: {file}",
                config={"foo.a-number": 123, "foo.a-bool": {"help": "Simply a boolean", "value": True}},
                overrides={
                    "foo.a-number": 456,
                    "foo.a-bool": False,
                    "other-lib.something-else": "blah",
                    "target.features_add": ["FOO"],
                },
                macros=["MACRO=1"],
            ),
        )

    def test_from_mbed_app(self):
        with tempfile.TemporaryDirectory() as directory:
            data = {
                "config": {"a-bool": False, "a-number": {"help": "Simply a number", "value": 0}},
                "target_overrides": {
                    "*": {"a-bool": True, "target.features_add": ["HAT"]},
                    "NOT_THIS_TARGET": {"a-number": 999, "target.features_add": ["BOAT"]},
                    "THIS_TARGET": {"a-number": 2, "some-lib.something-else": "blah"},
                },
                "macros": ["SOME_MACRO=2"],
            }
            file = pathlib.Path(directory, "mbed_app.json")
            file.write_text(json.dumps(data))

            subject = Source.from_mbed_app(file, ["THIS_TARGET"])

        self.assertEqual(
            subject,
            Source(
                human_name=f"File: {file}",
                config={"app.a-bool": False, "app.a-number": {"help": "Simply a number", "value": 0}},
                overrides={
                    "app.a-number": 2,
                    "app.a-bool": True,
                    "some-lib.something-else": "blah",
                    "target.features_add": ["HAT"],
                },
                macros=["SOME_MACRO=2"],
            ),
        )

    def test_from_target(self):
        # Warning: Target is a dataclass and dataclasses provide no type safety when mocking
        target = dict(
            features={"feature_1"},
            components={"component_1"},
            labels={"label_1"},
            extra_labels={"label_2"},
            config={"foo": "bar", "target.bool": True},
            macros=["MACRO_A"],
        )

        subject = Source.from_target(target)

        self.assertEqual(
            subject,
            Source(
                human_name=f"mbed_target.Target for {target}",
                config={"target.foo": "bar", "target.bool": True},
                overrides={
                    "target.features": target["features"],
                    "target.components": target["components"],
                    "target.labels": target["labels"],
                    "target.extra_labels": target["extra_labels"],
                    "target.macros": target["macros"],
                },
                macros=[],
            ),
        )


class TestFilterTargetOverrides(TestCase):
    def test_returns_overrides_only_for_given_labels(self):
        subject = _filter_target_overrides(
            {"*": {"number": 123}, "B_TARGET": {"string": "boat"}, "A_TARGET": {"bool": True}}, ["A_TARGET"]
        )

        self.assertEqual(subject, {"number": 123, "bool": True})


class TestNamespaceData(TestCase):
    def test_prefixes_keys_without_namespace(self):
        data = {
            "foo": True,
            "hat.bar": 123,
        }

        self.assertEqual(_namespace_data(data, "my-prefix"), {"my-prefix.foo": True, "hat.bar": 123})


class TestDecodeJSONFile(TestCase):
    def test_logs_path_and_raises_when_decode_fails(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            text = "This is not valid JSON<>>"
            tmp_file = pathlib.Path(tmp_dir, "mbed_lib.json")
            tmp_file.write_text(text)

            with self.assertRaises(json.JSONDecodeError):
                with self.assertLogs(level="ERROR") as logger:
                    _decode_json_file(tmp_file)

                    self.assertIn(str(tmp_file), logger.output)
