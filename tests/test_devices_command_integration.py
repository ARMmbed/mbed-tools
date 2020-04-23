#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase, mock

import click
from click.testing import CliRunner

from mbed_tools.cli import cli
from mbed_devices.mbed_tools import cli as mbed_devices_cli
from mbed_tools_lib.exceptions import ToolsError


class TestDevicesCommandIntegration(TestCase):
    def test_devices_is_integrated(self):
        self.assertEqual(cli.commands["devices"], mbed_devices_cli)


class TestClickGroupWithExceptionHandling(TestCase):
    @mock.patch("mbed_tools.cli.LOGGER.error", autospec=True)
    def test_logs_tools_errors(self, logger_error):
        def callback():
            raise ToolsError()

        mock_cli = click.Command("test", callback=callback)
        cli.add_command(mock_cli, "test")

        CliRunner().invoke(cli, ["test"])

        logger_error.assert_called_once()


class TestVersionCommand(TestCase):
    def test_version_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        self.assertIn("mbed-tools", result.output)
        self.assertEqual(0, result.exit_code)
