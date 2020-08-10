#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from mbed_tools.build._internal.config.assemble_build_config import (
    _assemble_config_from_sources_and_lib_files,
    assemble_config,
)
from mbed_tools.build._internal.config.config import Config
from mbed_tools.build._internal.find_files import find_files
from mbed_tools.build._internal.config.source import Source


def create_files(directory, files):
    created_files = []
    for file in files:
        path = Path(directory, file["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(file["json_contents"]))
        created_files.append(path)
    return created_files


@mock.patch("mbed_tools.build._internal.config.assemble_build_config.Source", autospec=True)
@mock.patch("mbed_tools.build._internal.config.assemble_build_config.find_files", autospec=True)
@mock.patch(
    "mbed_tools.build._internal.config.assemble_build_config._assemble_config_from_sources_and_lib_files", autospec=True
)
class TestAssembleConfig(TestCase):
    def test_calls_collaborator_with_source_and_file_paths(
        self, _assemble_config_from_sources_and_lib_files, find_files, Source,
    ):
        mbed_target = dict()
        mbed_program_directory = Path("foo")
        app_config_file = mbed_program_directory / "mbed_app.json"

        subject = assemble_config(mbed_target, mbed_program_directory, app_config_file)

        self.assertEqual(subject, _assemble_config_from_sources_and_lib_files.return_value)
        _assemble_config_from_sources_and_lib_files.assert_called_once_with(
            mbed_target, find_files.return_value, app_config_file
        )
        find_files.assert_called_once_with("mbed_lib.json", mbed_program_directory)


class TestAssembleConfigFromSourcesAndLibFiles(TestCase):
    def test_assembles_config_using_all_relevant_files(self):
        target = {
            "config": {"foo": None},
            "macros": {},
            "labels": set("A"),
            "extra_labels": set(),
            "features": set("RED"),
            "components": set(),
        }
        mbed_lib_files = [
            {
                "path": Path("TARGET_A", "mbed_lib.json"),
                "json_contents": {
                    "name": "a",
                    "config": {"number": 123},
                    "target_overrides": {"*": {"target.features_add": ["RED"]}},
                },
            },
            {
                "path": Path("subdir", "FEATURE_RED", "mbed_lib.json"),
                "json_contents": {
                    "name": "red",
                    "config": {"bool": False},
                    "target_overrides": {
                        "A": {"bool": True, "target.features_add": ["BLUE"], "target.components_add": ["LEG"]}
                    },
                    "macros": ["RED_MACRO"],
                },
            },
            {
                "path": Path("COMPONENT_LEG", "mbed_lib.json"),
                "json_contents": {"name": "leg", "config": {"number-of-fingers": 5}, "macros": ["LEG_MACRO"]},
            },
        ]
        unused_mbed_lib_file = {
            "path": Path("subdir", "FEATURE_BROWN", "mbed_lib.json"),
            "json_contents": {
                "name": "brown",
                "target_overrides": {"*": {"red.bool": "DON'T USE ME"}},
                "macros": ["DONT_USE_THIS_MACRO"],
            },
        }
        mbed_app_file = {
            "path": Path("mbed_app.json"),
            "json_contents": {"target_overrides": {"*": {"target.foo": "bar"}}},
        }

        with TemporaryDirectory() as directory:
            created_mbed_lib_files = create_files(directory, mbed_lib_files)
            created_mbed_app_file = create_files(directory, [mbed_app_file])[0]
            create_files(directory, [unused_mbed_lib_file])

            subject = _assemble_config_from_sources_and_lib_files(
                target, find_files("mbed_lib.json", Path(directory)), created_mbed_app_file
            )

            mbed_lib_sources = [Source.from_mbed_lib(Path(directory, file), ["A"]) for file in created_mbed_lib_files]
            mbed_app_source = Source.from_mbed_app(created_mbed_app_file, ["A"])
            expected_config = Config.from_sources([Source.from_target(target)] + mbed_lib_sources + [mbed_app_source])

            self.assertEqual(subject, expected_config)

    def test_updates_target_labels_from_config(self):
        target = {
            "config": {"foo": None},
            "macros": {"NO"},
            "labels": set("A"),
            "extra_labels": set(),
            "features": set(),
            "components": set(),
        }
        mbed_lib_files = [
            {
                "path": Path("TARGET_A", "mbed_lib.json"),
                "json_contents": {"name": "a", "target_overrides": {"*": {"target.features_add": ["RED"]}}},
            },
            {
                "path": Path("subdir", "FEATURE_RED", "mbed_lib.json"),
                "json_contents": {
                    "name": "red",
                    "target_overrides": {
                        "A": {
                            "target.macros_remove": ["NO"],
                            "target.features_add": ["BLUE"],
                            "target.components_add": ["LEG"],
                        }
                    },
                    "macros": ["RED_MACRO"],
                },
            },
        ]
        mbed_app_file = {
            "path": Path("mbed_app.json"),
            "json_contents": {
                "target_overrides": {
                    "*": {
                        "target.foo": "bar",
                        "target.labels_add": ["PICKLE"],
                        "target.extra_labels_add": ["EXTRA_HOT"],
                        "target.macros_add": ["TICKER"],
                    }
                }
            },
        }

        with TemporaryDirectory() as directory:
            _ = create_files(directory, mbed_lib_files)
            created_mbed_app_file = create_files(directory, [mbed_app_file])[0]

            _ = _assemble_config_from_sources_and_lib_files(
                target, find_files("mbed_lib.json", Path(directory)), created_mbed_app_file
            )

            self.assertEqual(target["features"], {"RED", "BLUE"})
            self.assertEqual(target["components"], {"LEG"})
            self.assertEqual(target["extra_labels"], {"EXTRA_HOT"})
            self.assertEqual(target["labels"], {"A", "PICKLE"})
            self.assertEqual(target["macros"], {"TICKER"})
