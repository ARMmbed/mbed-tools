#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

import pytest

from unittest import mock

from mbed_tools.project import initialise_project, import_project, deploy_project, get_known_libs


@pytest.fixture
def mock_program():
    with mock.patch("mbed_tools.project.project.MbedProgram") as prog:
        yield prog


@pytest.fixture
def mock_git():
    with mock.patch("mbed_tools.project.project.git_utils") as gutils:
        yield gutils


class TestInitialiseProject:
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


class TestImportProject:
    def test_clones_from_remote(self, mock_program):
        url = "https://git.com/gitorg/repo"
        import_project(url, recursive=False)

        mock_program.from_url.assert_called_once_with(url, pathlib.Path(url.rsplit("/", maxsplit=1)[-1]))

    def test_resolves_libs_when_recursive_is_true(self, mock_program):
        url = "https://git.com/gitorg/repo"
        import_project(url, recursive=True)

        mock_program.from_url.assert_called_once_with(url, pathlib.Path(url.rsplit("/", maxsplit=1)[-1]))
        mock_program.from_url.return_value.resolve_libraries.assert_called_once()


class TestDeployProject:
    def test_checks_out_libraries(self, mock_program):
        path = pathlib.Path("somewhere")
        deploy_project(path, force=False)

        mock_program.from_existing.assert_called_once_with(path, check_mbed_os=False)
        mock_program.from_existing.return_value.deploy_libraries.assert_called_once_with(force=False)

    def test_resolves_libs_if_unresolved_detected(self, mock_program):
        path = pathlib.Path("somewhere")
        deploy_project(path)

        mock_program.from_existing.return_value.resolve_libraries.assert_called_once()


class TestPrintLibs:
    def test_list_libraries_called(self, mock_program):
        path = pathlib.Path("somewhere")
        get_known_libs(path)

        mock_program.from_existing.assert_called_once_with(path, check_mbed_os=False)
        mock_program.from_existing.return_value.list_known_library_dependencies.assert_called()
