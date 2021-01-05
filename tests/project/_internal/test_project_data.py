#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tests for project_data.py."""
import pathlib

from unittest import TestCase, mock

from mbed_tools.project._internal.project_data import (
    MbedProgramFiles,
    MbedOS,
    MAIN_CPP_FILE_NAME,
)
from tests.project.factories import make_mbed_lib_reference, make_mbed_program_files, make_mbed_os_files, patchfs


class TestMbedProgramFiles(TestCase):
    @patchfs
    def test_from_new_raises_if_program_files_already_exist(self, fs):
        root = pathlib.Path(fs, "foo")
        make_mbed_program_files(root)

        with self.assertRaises(ValueError):
            MbedProgramFiles.from_new(root)

    @patchfs
    def test_from_new_returns_valid_program_file_set(self, fs):
        root = pathlib.Path(fs, "foo")
        root.mkdir()

        program = MbedProgramFiles.from_new(root)

        self.assertTrue(program.app_config_file.exists())
        self.assertTrue(program.mbed_os_ref.exists())
        self.assertTrue(program.cmakelists_file.exists())

    @patchfs
    def test_from_new_calls_render_template_for_gitignore_cmake_and_main(self, fs):
        with mock.patch(
            "mbed_tools.project._internal.project_data.render_cmakelists_template"
        ) as render_cmakelists_template:
            with mock.patch(
                "mbed_tools.project._internal.project_data.render_main_cpp_template"
            ) as render_main_cpp_template:
                with mock.patch(
                    "mbed_tools.project._internal.project_data.render_gitignore_template"
                ) as render_gitignore_template:
                    root = pathlib.Path(fs, "foo")
                    root.mkdir()
                    program_files = MbedProgramFiles.from_new(root)
                    render_cmakelists_template.assert_called_once_with(program_files.cmakelists_file, "foo")
                    render_main_cpp_template.assert_called_once_with(root / MAIN_CPP_FILE_NAME)
                    render_gitignore_template.assert_called_once_with(root / ".gitignore")

    @patchfs
    def test_from_existing_finds_existing_program_data(self, fs):
        root = pathlib.Path(fs, "foo")
        make_mbed_program_files(root)

        program = MbedProgramFiles.from_existing(root)

        self.assertTrue(program.app_config_file.exists())
        self.assertTrue(program.mbed_os_ref.exists())
        self.assertTrue(program.cmakelists_file.exists())


class TestMbedLibReference(TestCase):
    @patchfs
    def test_is_resolved_returns_true_if_source_code_dir_exists(self, fs):
        root = pathlib.Path(fs, "foo")
        lib = make_mbed_lib_reference(root, resolved=True)

        self.assertTrue(lib.is_resolved())

    @patchfs
    def test_is_resolved_returns_false_if_source_code_dir_doesnt_exist(self, fs):
        root = pathlib.Path(fs, "foo")
        lib = make_mbed_lib_reference(root)

        self.assertFalse(lib.is_resolved())

    @patchfs
    def test_get_git_reference_returns_lib_file_contents(self, fs):
        root = pathlib.Path(fs, "foo")
        url = "https://github.com/mylibrepo"
        ref = "latest"
        references = [f"{url}#{ref}", f"{url}/#{ref}"]

        for full_ref in references:
            lib = make_mbed_lib_reference(root, ref_url=full_ref)

            reference = lib.get_git_reference()

            self.assertEqual(reference.repo_url, url)
            self.assertEqual(reference.ref, ref)


class TestMbedOS(TestCase):
    @patchfs
    def test_from_existing_finds_existing_mbed_os_data(self, fs):
        root_path = pathlib.Path(fs, "my-version-of-mbed-os")
        make_mbed_os_files(root_path)

        mbed_os = MbedOS.from_existing(root_path)

        self.assertEqual(mbed_os.targets_json_file, root_path / "targets" / "targets.json")

    @patchfs
    def test_raises_if_files_missing(self, fs):
        root_path = pathlib.Path(fs, "my-version-of-mbed-os")
        root_path.mkdir()

        with self.assertRaises(ValueError):
            MbedOS.from_existing(root_path)
