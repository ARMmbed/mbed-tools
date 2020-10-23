#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import os
import pathlib

from unittest import mock, TestCase

from mbed_tools.project import MbedProgram
from mbed_tools.project.exceptions import ExistingProgram, ProgramNotFound, MbedOSNotFound
from mbed_tools.project.mbed_program import _find_program_root, parse_url
from mbed_tools.project._internal.project_data import MbedProgramFiles
from tests.project.factories import make_mbed_program_files, make_mbed_os_files, make_mbed_lib_reference, patchfs


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
    @mock.patch("mbed_tools.project.mbed_program.git_utils.clone", autospec=True)
    def test_from_url_returns_valid_program(self, mock_clone, fs):
        fs_root = pathlib.Path(fs, "foo")
        url = "https://valid"
        mock_clone.side_effect = lambda *args: make_mbed_program_files(fs_root)
        program = MbedProgram.from_url(url, fs_root)

        self.assertEqual(program.files, MbedProgramFiles.from_existing(fs_root))
        mock_clone.assert_called_once_with(url, fs_root)

    @patchfs
    @mock.patch("mbed_tools.project.mbed_program.git_utils.clone", autospec=True)
    def test_from_url_does_not_raise_with_odd_program_layout(self, mock_clone, fs):
        fs_root = pathlib.Path(fs, "foo")
        fs_root.mkdir()
        url = "https://nested"
        mock_clone.side_effect = lambda *args: make_mbed_program_files(fs_root / "nested")
        MbedProgram.from_url(url, fs_root)

        mock_clone.assert_called_once_with(url, fs_root)

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


class TestLibReferenceHandling(TestCase):
    @mock.patch("mbed_tools.project.mbed_program.LibraryReferences", autospec=True)
    @mock.patch("mbed_tools.project.mbed_program.MbedProgramFiles")
    @mock.patch("mbed_tools.project.mbed_program.MbedOS")
    def test_resolve_libraries_delegation(self, mbed_os, mbed_program_files, mock_lib_refs):
        program = MbedProgram(mbed_program_files(), mbed_os())
        program.resolve_libraries()

        program.lib_references.resolve.assert_called_once()

    @mock.patch("mbed_tools.project.mbed_program.LibraryReferences", autospec=True)
    @mock.patch("mbed_tools.project.mbed_program.MbedProgramFiles")
    @mock.patch("mbed_tools.project.mbed_program.MbedOS")
    def test_checkout_libraries_delegation(self, mbed_os, mbed_program_files, mock_lib_refs):
        program = MbedProgram(mbed_program_files(), mbed_os())
        program.checkout_libraries()

        program.lib_references.checkout.assert_called_once()

    @patchfs
    def test_lists_all_known_libraries(self, fs):
        root = pathlib.Path(fs, "root").absolute().resolve()
        make_mbed_program_files(root)
        lib_ref = make_mbed_lib_reference(root, resolved=True, ref_url="https://blah")
        lib_ref_unresolved = make_mbed_lib_reference(
            root, name="my-unresolved-lib.lib", resolved=False, ref_url="https://blah"
        )

        program = MbedProgram.from_existing(root, check_mbed_os=False)
        libs = program.list_known_library_dependencies()

        self.assertEqual(str(lib_ref_unresolved), str(libs[1]))
        self.assertEqual(str(lib_ref), str(libs[2]))

    @patchfs
    def test_checks_for_unresolved_libraries(self, fs):
        root = pathlib.Path(fs, "root").absolute().resolve()
        make_mbed_program_files(root)
        make_mbed_lib_reference(root, resolved=True, ref_url="https://blah")
        make_mbed_lib_reference(root, name="my-unresolved-lib.lib", resolved=False, ref_url="https://blah")

        program = MbedProgram.from_existing(root, check_mbed_os=False)

        self.assertTrue(program.has_unresolved_libraries())


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
