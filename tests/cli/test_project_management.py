#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import TestCase, mock

from click.testing import CliRunner

from mbed_tools.cli.project_management import new, clone, deploy, libs


@mock.patch("mbed_tools.cli.project_management.initialise_project", autospec=True)
class TestNewCommand(TestCase):
    def test_calls_new_function_with_correct_args(self, mock_initialise_project):
        CliRunner().invoke(new, ["path", "--create-only"])
        mock_initialise_project.assert_called_once_with(pathlib.Path("path"), True)

    def test_echos_mbed_os_message_when_required(self, mock_initialise_project):
        result = CliRunner().invoke(new, ["path"])

        self.assertEqual(
            result.output,
            "Creating a new Mbed program at path 'path'.\nDownloading mbed-os and adding it to the project.\n",
        )


@mock.patch("mbed_tools.cli.project_management.clone_project", autospec=True)
class TestCloneCommand(TestCase):
    def test_calls_clone_function_with_correct_args(self, mocked_clone_project):
        CliRunner().invoke(clone, ["url", "dst"])
        mocked_clone_project.assert_called_once_with("url", pathlib.Path("dst"), True)


@mock.patch("mbed_tools.cli.project_management.get_known_libs", autospec=True)
class TestLibsCommand(TestCase):
    def test_calls_libs_function(self, mocked_get_libs):
        CliRunner().invoke(libs)
        mocked_get_libs.assert_called_once()


@mock.patch("mbed_tools.cli.project_management.deploy_project", autospec=True)
class TestDeployCommand(TestCase):
    def test_calls_deploy_function_with_correct_args(self, mocked_deploy_project):
        CliRunner().invoke(deploy, ["path", "--force"])
        mocked_deploy_project.assert_called_once_with(pathlib.Path("path"), True)
