#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase, mock

from click.testing import CliRunner

from mbed_tools.cli.configure import configure


class TestConfigureCommand(TestCase):
    @mock.patch("mbed_tools.cli.configure.generate_config")
    @mock.patch("mbed_tools.cli.configure.MbedProgram")
    def test_generate_config_called_with_correct_arguments(self, program, generate_config):
        CliRunner().invoke(configure, ["-m", "k64f", "-t", "gcc_arm"])

        generate_config.assert_called_once_with("K64F", "GCC_ARM", program.from_existing())

    @mock.patch("mbed_tools.cli.configure.generate_config")
    @mock.patch("mbed_tools.cli.configure.MbedProgram")
    def test_generate_config_called_with_mbed_os_path(self, program, generate_config):
        CliRunner().invoke(configure, ["-m", "k64f", "-t", "gcc_arm", "--mbed-os-path", "./extern/mbed-os"])

        generate_config.assert_called_once_with("K64F", "GCC_ARM", program.from_existing())
