#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase, mock

from mbed_tools.build import generate_config


class TestGenerateConfig(TestCase):
    @mock.patch("mbed_tools.build.config.MbedProgram")
    @mock.patch("mbed_tools.build.config.get_target_by_name")
    @mock.patch("mbed_tools.build.config.generate_mbed_config_cmake_file")
    @mock.patch("mbed_tools.build.config.assemble_config")
    @mock.patch("mbed_tools.build.config.write_file")
    def test_collaborators_called_with_corrrect_arguments(
        self, write_file, assemble_config, gen_config_cmake, get_target_by_name, mbed_program
    ):
        program = mbed_program.from_existing()

        generate_config("K64F", "GCC_ARM", program)

        get_target_by_name.assert_called_once_with("K64F", program.mbed_os.targets_json_file)
        assemble_config.assert_called_once_with(
            get_target_by_name.return_value, program.root, program.files.app_config_file,
        )
        gen_config_cmake.assert_called_once_with(
            "K64F", get_target_by_name.return_value, assemble_config.return_value, "GCC_ARM"
        )
        write_file.assert_called_once_with(
            program.files.cmake_config_file.parent, program.files.cmake_config_file.name, gen_config_cmake.return_value,
        )
