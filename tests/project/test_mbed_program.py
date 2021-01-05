#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import os
import pathlib

from unittest import TestCase

from mbed_tools.project import MbedProgram
from mbed_tools.project.exceptions import ExistingProgram, ProgramNotFound, MbedOSNotFound
from mbed_tools.project.mbed_program import _find_program_root, parse_url
from mbed_tools.project._internal.project_data import MbedProgramFiles
from tests.project.factories import make_mbed_program_files, make_mbed_os_files, patchfs


class TestInitialiseProgram(TestCase):
    @patchfs
    def test_from_new_local_dir_raises_if_path_is_existing_program(self, fs):
        program_root = pathlib.Path(fs, "programfoo")
        program_root.mkdir()
        (program_root / "mbed-os.lib").touch()

        with self.assertRaises(ExistingProgram):
            MbedProgram.from_new(program_root)

    @patchfs
    def test_from_new_local_dir_generates_valid_program_creating_directory(self, fs):
        fs_root = pathlib.Path(fs, "foo")
        fs_root.mkdir()
        program_root = fs_root / "programfoo"

        program = MbedProgram.from_new(program_root)

        self.assertEqual(program.files, MbedProgramFiles.from_existing(program_root))

    @patchfs
    def test_from_new_local_dir_generates_valid_program_creating_directory_in_cwd(self, fs):
        old_cwd = os.getcwd()
        try:
            fs_root = pathlib.Path(fs, "foo")
            fs_root.mkdir()
            os.chdir(fs_root)
            program_root = pathlib.Path("programfoo")

            program = MbedProgram.from_new(program_root)

            self.assertEqual(program.files, MbedProgramFiles.from_existing(program_root))
        finally:
            os.chdir(old_cwd)

    @patchfs
    def test_from_new_local_dir_generates_valid_program_existing_directory(self, fs):
        fs_root = pathlib.Path(fs, "foo")
        fs_root.mkdir()
        program_root = fs_root / "programfoo"
        program_root.mkdir()

        program = MbedProgram.from_new(program_root)

        self.assertEqual(program.files, MbedProgramFiles.from_existing(program_root))

    @patchfs
    def test_from_existing_raises_if_path_is_not_a_program(self, fs):
        fs_root = pathlib.Path(fs, "foo")
        fs_root.mkdir()
        program_root = fs_root / "programfoo"

        with self.assertRaises(ProgramNotFound):
            MbedProgram.from_existing(program_root)

    @patchfs
    def test_from_existing_raises_if_no_mbed_os_dir_found_and_check_mbed_os_is_true(self, fs):
        fs_root = pathlib.Path(fs, "foo")
        make_mbed_program_files(fs_root)

        with self.assertRaises(MbedOSNotFound):
            MbedProgram.from_existing(fs_root, check_mbed_os=True)

    @patchfs
    def test_from_existing_returns_valid_program(self, fs):
        fs_root = pathlib.Path(fs, "foo")
        make_mbed_program_files(fs_root)
        make_mbed_os_files(fs_root / "mbed-os")

        program = MbedProgram.from_existing(fs_root)

        self.assertTrue(program.files.app_config_file.exists())
        self.assertTrue(program.mbed_os.root.exists())

    @patchfs
    def test_from_existing_with_mbed_os_path_returns_valid_program(self, fs):
        fs_root = pathlib.Path(fs, "foo")
        mbed_os_path = fs_root / "extern/mbed-os"
        mbed_os_path.mkdir(parents=True)
        make_mbed_program_files(fs_root)
        make_mbed_os_files(mbed_os_path)

        program = MbedProgram.from_existing(fs_root, mbed_os_path)

        self.assertTrue(program.files.app_config_file.exists())
        self.assertTrue(program.mbed_os.root.exists())


class TestParseURL(TestCase):
    def test_creates_url_and_dst_dir_from_name(self):
        name = "mbed-os-example-blows-up-board"
        data = parse_url(name)

        self.assertEqual(data["url"], f"https://github.com/armmbed/{name}")
        self.assertEqual(data["dst_path"], name)

    def test_creates_valid_dst_dir_from_url(self):
        url = "https://superversioncontrol/superorg/mbed-os-example-numskull"
        data = parse_url(url)

        self.assertEqual(data["url"], url)
        self.assertEqual(data["dst_path"], "mbed-os-example-numskull")


class TestFindProgramRoot(TestCase):
    @patchfs
    def test_finds_program_higher_in_dir_tree(self, fs):
        program_root = pathlib.Path(fs, "foo")
        pwd = program_root / "subprojfoo" / "libbar"
        make_mbed_program_files(program_root)
        pwd.mkdir(parents=True)

        self.assertEqual(_find_program_root(pwd), program_root.resolve())

    @patchfs
    def test_finds_program_at_current_path(self, fs):
        program_root = pathlib.Path(fs, "foo")
        make_mbed_program_files(program_root)

        self.assertEqual(_find_program_root(program_root), program_root.resolve())

    @patchfs
    def test_raises_if_no_program_found(self, fs):
        program_root = pathlib.Path(fs, "foo")
        program_root.mkdir()

        with self.assertRaises(ProgramNotFound):
            _find_program_root(program_root)
