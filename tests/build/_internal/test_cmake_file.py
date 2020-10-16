#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

from tests.build._internal.config.factories import ConfigFactory
from mbed_tools.build._internal.cmake_file import generate_mbed_config_cmake_file, _render_mbed_config_cmake_template


class TestGenerateCMakeListsFile(TestCase):
    def test_correct_arguments_passed(self):
        target = dict()
        target["labels"] = ["foo"]
        target["extra_labels"] = ["morefoo"]
        target["features"] = ["bar"]
        target["components"] = ["baz"]
        target["macros"] = ["macbaz"]
        target["device_has"] = ["stuff"]
        target["c_lib"] = ["c_lib"]
        target["core"] = ["core"]
        target["printf_lib"] = ["printf_lib"]
        target["supported_form_factors"] = ["arduino"]
        config = ConfigFactory()
        mbed_target = "K64F"
        toolchain_name = "GCC"
        target["supported_c_libs"] = {toolchain_name.lower(): ["small", "std"]}
        target["supported_application_profiles"] = ["full", "bare-metal"]

        result = generate_mbed_config_cmake_file(mbed_target, target, config, toolchain_name)

        self.assertEqual(
            result, _render_mbed_config_cmake_template(target, config, toolchain_name, mbed_target,),
        )


class TestRendersCMakeListsFile(TestCase):
    def test_returns_rendered_content(self):
        target = dict()
        target["labels"] = ["foo"]
        target["extra_labels"] = ["morefoo"]
        target["features"] = ["bar"]
        target["components"] = ["baz"]
        target["macros"] = ["macbaz"]
        target["device_has"] = ["stuff"]
        target["core"] = ["core"]
        target["c_lib"] = ["c_lib"]
        target["printf_lib"] = ["printf_lib"]
        target["supported_form_factors"] = ["arduino"]
        config = ConfigFactory()
        toolchain_name = "baz"
        target["supported_c_libs"] = {toolchain_name.lower(): ["small", "std"]}
        target["supported_application_profiles"] = ["full", "bare-metal"]
        result = _render_mbed_config_cmake_template(target, config, toolchain_name, "target_name")

        for label in target["labels"] + target["extra_labels"]:
            self.assertIn(label, result)

        for macro in target["features"] + target["components"] + [toolchain_name]:
            self.assertIn(macro, result)

        for toolchain in target["supported_c_libs"]:
            self.assertIn(toolchain, result)
            for supported_c_libs in toolchain:
                self.assertIn(supported_c_libs, result)

        for supported_application_profiles in target["supported_application_profiles"]:
            self.assertIn(supported_application_profiles, result)
