#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import TestCase, mock

from mbed_tools.project import initialise_project, clone_project, checkout_project_revision, get_known_libs


@mock.patch("mbed_tools.project.project.MbedProgram", autospec=True)
class TestInitialiseProject(TestCase):
    def test_fetches_mbed_os_when_create_only_is_false(self, mock_program):
        path = pathlib.Path()
        initialise_project(path, create_only=False)

        mock_program.from_new.assert_called_once_with(path)
        mock_program.from_new.return_value.resolve_libraries.assert_called_once()

    def test_skips_mbed_os_when_create_only_is_true(self, mock_program):
        path = pathlib.Path()
        initialise_project(path, create_only=True)

        mock_program.from_new.assert_called_once_with(path)
        mock_program.from_new.return_value.resolve_libraries.assert_not_called()


@mock.patch("mbed_tools.project.project.MbedProgram", autospec=True)
class TestCloneProject(TestCase):
    def test_clones_from_remote(self, mock_program):
        url = "https://git.com/gitorg/repo"
        clone_project(url, recursive=False)

        mock_program.from_url.assert_called_once_with(url, pathlib.Path(url.rsplit("/", maxsplit=1)[-1]))

    def test_resolves_libs_when_recursive_is_true(self, mock_program):
        url = "https://git.com/gitorg/repo"
        clone_project(url, recursive=True)

        mock_program.from_url.assert_called_once_with(url, pathlib.Path(url.rsplit("/", maxsplit=1)[-1]))
        mock_program.from_url.return_value.resolve_libraries.assert_called_once()


@mock.patch("mbed_tools.project.project.MbedProgram", autospec=True)
class TestCheckoutProject(TestCase):
    def test_checks_out_libraries(self, mock_program):
        path = pathlib.Path("somewhere")
        checkout_project_revision(path, force=False)

        mock_program.from_existing.assert_called_once_with(path, False)
        mock_program.from_existing.return_value.checkout_libraries.assert_called_once_with(force=False)

    def test_resolves_libs_if_unresolved_detected(self, mock_program):
        path = pathlib.Path("somewhere")
        checkout_project_revision(path)

        mock_program.from_existing.return_value.resolve_libraries.assert_called_once()


@mock.patch("mbed_tools.project.project.MbedProgram", autospec=True)
class TestPrintLibs(TestCase):
    def test_list_libraries_called(self, mock_program):
        path = pathlib.Path("somewhere")
        get_known_libs(path)

        mock_program.from_existing.assert_called_once_with(path, False)
        mock_program.from_existing.return_value.list_known_library_dependencies.assert_called()
