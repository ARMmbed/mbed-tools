#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pytest

from tests.build._internal.config.factories import ConfigFactory, SourceFactory
from mbed_tools.build._internal.cmake_file import generate_mbed_config_cmake_file, _render_mbed_config_cmake_template
from mbed_tools.build._internal.config.config import _create_config_option


TOOLCHAIN_NAME = "gcc"


@pytest.fixture()
def fake_target():
    return {
        "labels": ["foo"],
        "extra_labels": ["morefoo"],
        "features": ["bar"],
        "components": ["baz"],
        "macros": ["macbaz"],
        "device_has": ["stuff"],
        "c_lib": ["c_lib"],
        "core": ["core"],
        "printf_lib": ["printf_lib"],
        "supported_form_factors": ["arduino"],
        "supported_c_libs": {TOOLCHAIN_NAME: ["ginormous"]},
        "supported_application_profiles": ["full", "bare-metal"],
    }


class TestGenerateCMakeListsFile:
    def test_correct_arguments_passed(self, fake_target):
        config = ConfigFactory()
        mbed_target = "K64F"

        result = generate_mbed_config_cmake_file(mbed_target, fake_target, config, TOOLCHAIN_NAME)

        assert result == _render_mbed_config_cmake_template(fake_target, config, TOOLCHAIN_NAME, mbed_target,)


class TestRendersCMakeListsFile:
    def test_returns_rendered_content(self, fake_target):
        config = ConfigFactory()
        result = _render_mbed_config_cmake_template(fake_target, config, TOOLCHAIN_NAME, "target_name")

        for label in fake_target["labels"] + fake_target["extra_labels"]:
            assert label in result

        for macro in fake_target["features"] + fake_target["components"] + [TOOLCHAIN_NAME]:
            assert macro in result

        for toolchain in fake_target["supported_c_libs"]:
            assert toolchain in result
            for supported_c_libs in toolchain:
                assert supported_c_libs in result

        for supported_application_profiles in fake_target["supported_application_profiles"]:
            assert supported_application_profiles in result

    def test_returns_quoted_content(self, fake_target):
        config = ConfigFactory()
        source = SourceFactory()

        # Add an option whose value contains quotes to the config.
        _create_config_option(config, "iotc-mqtt-host", '{"mqtt.2030.ltsapis.goog", IOTC_MQTT_PORT}', source)

        result = _render_mbed_config_cmake_template(fake_target, config, TOOLCHAIN_NAME, "target_name")
        assert '"-DMBED_CONF_IOTC_MQTT_HOST={\\"mqtt.2030.ltsapis.goog\\", IOTC_MQTT_PORT}"' in result
