#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import TestCase, mock

from tests.build._internal.config.factories import ConfigFactory
from mbed_tools.build._internal.cmake_file import generate_mbed_config_cmake_file, _render_mbed_config_cmake_template


class TestGenerateCMakeListsFile(TestCase):
    @mock.patch("mbed_tools.build._internal.cmake_file.datetime")
    @mock.patch("mbed_tools.build._internal.cmake_file.assemble_config")
    @mock.patch("mbed_tools.build._internal.cmake_file.get_target_by_name")
    def test_correct_arguments_passed(self, get_target_by_name, assemble_config, datetime):
        target = mock.Mock()
        target.labels = ["foo"]
        target.features = ["bar"]
        target.components = ["baz"]
        target.macros = ["macbaz"]
        target.device_has = ["stuff"]
        target.core = ["core"]
        target.supported_form_factors = ["arduino"]
        datetime = mock.Mock()
        datetime.datetime.now.return_value.timestamp.return_value = 2
        config = ConfigFactory()
        assemble_config.return_value = config
        get_target_by_name.return_value = target
        mbed_target = "K64F"
        program_path = "blinky"
        toolchain_name = "GCC"

        result = generate_mbed_config_cmake_file(mbed_target, program_path, toolchain_name)

        get_target_by_name.assert_called_once_with(mbed_target, program_path)
        assemble_config.assert_called_once_with(mbed_target, pathlib.Path(program_path))
        self.assertEqual(
            result, _render_mbed_config_cmake_template(target, config, toolchain_name, mbed_target,),
        )


class TestRendersCMakeListsFile(TestCase):
    def test_returns_rendered_content(self):
        target = mock.Mock()
        target.labels = ["foo"]
        target.features = ["bar"]
        target.components = ["baz"]
        target.macros = ["macbaz"]
        target.device_has = ["stuff"]
        target.core = ["core"]
        target.supported_form_factors = ["arduino"]
        config = ConfigFactory()
        toolchain_name = "baz"
        result = _render_mbed_config_cmake_template(target, config, toolchain_name, "target_name")

        for label in target.labels:
            self.assertIn(label, result)

        for macro in target.features + target.components + [toolchain_name]:
            self.assertIn(macro.upper(), result)
