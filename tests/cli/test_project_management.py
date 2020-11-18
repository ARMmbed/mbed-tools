#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import mock

import pytest

from click.testing import CliRunner

from mbed_tools.cli.project_management import new, import_, deploy, libs


@pytest.fixture
def mock_initialise_project():
    with mock.patch("mbed_tools.cli.project_management.initialise_project") as init_proj:
        yield init_proj


@pytest.fixture
def mock_import_project():
    with mock.patch("mbed_tools.cli.project_management.import_project") as import_proj:
        yield import_proj


@pytest.fixture
def mock_deploy_project():
    with mock.patch("mbed_tools.cli.project_management.deploy_project") as deploy_proj:
        yield deploy_proj


@pytest.fixture
def mock_get_libs():
    with mock.patch("mbed_tools.cli.project_management.get_known_libs") as get_libs:
        yield get_libs


class TestNewCommand:
    def test_calls_new_function_with_correct_args(self, mock_initialise_project):
        CliRunner().invoke(new, ["path", "--create-only"])
        mock_initialise_project.assert_called_once_with(pathlib.Path("path"), True)

    def test_echos_mbed_os_message_when_required(self, mock_initialise_project):
        expected = "Creating a new Mbed program at path 'path'.\nDownloading mbed-os and adding it to the project.\n"

        result = CliRunner().invoke(new, ["path"])

        assert result.output == expected


class TestImportCommand:
    def test_calls_clone_function_with_correct_args(self, mock_import_project):
        CliRunner().invoke(import_, ["url", "dst"])
        mock_import_project.assert_called_once_with("url", pathlib.Path("dst"), True)


class TestLibsCommand:
    def test_calls_libs_function(self, mock_get_libs):
        CliRunner().invoke(libs)
        mock_get_libs.assert_called_once()


class TestDeployCommand:
    def test_calls_deploy_function_with_correct_args(self, mock_deploy_project):
        CliRunner().invoke(deploy, ["path", "--force"])
        mock_deploy_project.assert_called_once_with(pathlib.Path("path"), True)
