#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import TestCase, mock

from mbed_tools.project._internal.libraries import MbedLibReference, LibraryReferences
from tests.project.factories import make_mbed_lib_reference, patchfs


@mock.patch("mbed_tools.project._internal.git_utils.clone", autospec=True)
class TestLibraryReferences(TestCase):
    @patchfs
    def test_hydrates_top_level_library_references(self, mock_clone, fs):
        fs_root = pathlib.Path(fs, "foo")
        lib = make_mbed_lib_reference(fs_root, ref_url="https://git")
        mock_clone.side_effect = lambda url, dst_dir: dst_dir.mkdir()

        lib_refs = LibraryReferences(fs_root, ignore_paths=["mbed-os"])
        lib_refs.resolve()

        mock_clone.assert_called_once_with(lib.get_git_reference().repo_url, lib.source_code_path)
        self.assertTrue(lib.is_resolved())

    @patchfs
    def test_hydrates_recursive_dependencies(self, mock_clone, fs):
        fs_root = pathlib.Path(fs, "foo")
        lib = make_mbed_lib_reference(fs_root, ref_url="https://git")
        # Create a lib reference without touching the fs at this point, we want to mock the effects of a recursive
        # reference lookup and we need to assert the reference was resolved.
        lib2 = MbedLibReference(
            reference_file=(lib.source_code_path / "lib2.lib"), source_code_path=(lib.source_code_path / "lib2")
        )
        # Here we mock the effects of a recursive reference lookup. We create a new lib reference as a side effect of
        # the first call to the mock. Then we create the src dir, thus resolving the lib, on the second call.
        mock_clone.side_effect = lambda url, dst_dir: (
            make_mbed_lib_reference(pathlib.Path(dst_dir), name=lib2.reference_file.name, ref_url="https://valid2"),
            lib2.source_code_path.mkdir(),
        )

        lib_refs = LibraryReferences(fs_root, ignore_paths=["mbed-os"])
        lib_refs.resolve()

        self.assertTrue(lib.is_resolved())
        self.assertTrue(lib2.is_resolved())

    @patchfs
    @mock.patch("mbed_tools.project._internal.git_utils.checkout", autospec=True)
    @mock.patch("mbed_tools.project._internal.git_utils.init", autospec=True)
    def test_does_not_perform_checkout_if_no_git_ref_exists(self, mock_init, mock_checkout, mock_clone, fs):
        fs_root = pathlib.Path(fs, "foo")
        make_mbed_lib_reference(fs_root, ref_url="https://git", resolved=True)

        lib_refs = LibraryReferences(fs_root, ignore_paths=["mbed-os"])
        lib_refs.checkout(force=False)

        mock_checkout.assert_not_called()

    @patchfs
    @mock.patch("mbed_tools.project._internal.git_utils.checkout", autospec=True)
    @mock.patch("mbed_tools.project._internal.git_utils.init", autospec=True)
    def test_performs_checkout_if_git_ref_exists(self, mock_init, mock_checkout, mock_clone, fs):
        fs_root = pathlib.Path(fs, "foo")
        lib = make_mbed_lib_reference(fs_root, ref_url="https://git#lajdhalk234", resolved=True)

        lib_refs = LibraryReferences(fs_root, ignore_paths=["mbed-os"])
        lib_refs.checkout(force=False)

        mock_checkout.assert_called_once_with(mock_init.return_value, lib.get_git_reference().ref, force=False)

    @patchfs
    @mock.patch("mbed_tools.project._internal.git_utils.checkout", autospec=True)
    @mock.patch("mbed_tools.project._internal.git_utils.init", autospec=True)
    def test_resolve_does_not_perform_checkout_if_no_git_ref_exists(self, mock_init, mock_checkout, mock_clone, fs):
        fs_root = pathlib.Path(fs, "foo")
        make_mbed_lib_reference(fs_root, ref_url="https://git")
        mock_clone.side_effect = lambda url, dst_dir: dst_dir.mkdir()

        lib_refs = LibraryReferences(fs_root, ignore_paths=["mbed-os"])
        lib_refs.resolve()

        mock_checkout.assert_not_called()

    @patchfs
    @mock.patch("mbed_tools.project._internal.git_utils.checkout", autospec=True)
    @mock.patch("mbed_tools.project._internal.git_utils.init", autospec=True)
    def test_resolve_performs_checkout_if_git_ref_exists(self, mock_init, mock_checkout, mock_clone, fs):
        fs_root = pathlib.Path(fs, "foo")
        lib = make_mbed_lib_reference(fs_root, ref_url="https://git#lajdhalk234")
        mock_clone.side_effect = lambda url, dst_dir: dst_dir.mkdir()

        lib_refs = LibraryReferences(fs_root, ignore_paths=["mbed-os"])
        lib_refs.resolve()

        mock_checkout.assert_called_once_with(None, lib.get_git_reference().ref)

    @patchfs
    @mock.patch("mbed_tools.project._internal.git_utils.checkout", autospec=True)
    @mock.patch("mbed_tools.project._internal.git_utils.init", autospec=True)
    def test_does_not_resolve_references_in_ignore_paths(self, mock_init, mock_checkout, mock_clone, fs):
        fs_root = pathlib.Path(fs, "mbed-os")
        make_mbed_lib_reference(fs_root, ref_url="https://git#lajdhalk234")

        lib_refs = LibraryReferences(fs_root, ignore_paths=["mbed-os"])
        lib_refs.resolve()

        mock_clone.assert_not_called()
