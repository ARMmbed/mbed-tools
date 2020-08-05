#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import TestCase, mock

from click.testing import CliRunner

from mbed_tools.cli.configure import configure


class TestConfigureCommand(TestCase):
    @mock.patch("mbed_tools.cli.configure.MbedProgram")
    @mock.patch("mbed_tools.cli.configure.get_target_by_name")
    @mock.patch("mbed_tools.cli.configure.generate_mbed_config_cmake_file")
    @mock.patch("mbed_tools.cli.configure.assemble_config")
    @mock.patch("mbed_tools.cli.configure.Source")
    @mock.patch("mbed_tools.cli.configure.write_file")
    def test_collaborators_called_with_corrrect_arguments(
        self, write_file, source, assemble_config, gen_config_cmake, get_target_by_name, mbed_program
    ):
        CliRunner().invoke(configure, ["-m", "k64f", "-t", "GCC_ARM"])

        mbed_program.from_existing.assert_called_once_with(pathlib.Path("."))
        get_target_by_name.assert_called_once_with(
            "K64F", mbed_program.from_existing.return_value.mbed_os.targets_json_file
        )
        assemble_config.assert_called_once_with(
            source.from_target.return_value,
            mbed_program.from_existing.return_value.root,
            mbed_program.from_existing.return_value.files.app_config_file,
        )
        gen_config_cmake.assert_called_once_with(
            "K64F", get_target_by_name.return_value, assemble_config.return_value, "GCC_ARM"
        )
        write_file.assert_called_once_with(
            mbed_program.from_existing.return_value.root / ".mbedbuild",
            "mbed_config.cmake",
            gen_config_cmake.return_value,
        )
