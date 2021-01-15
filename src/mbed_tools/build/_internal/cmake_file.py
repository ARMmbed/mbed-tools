#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Module in charge of CMake file generation."""
import pathlib

import jinja2

from mbed_tools.build._internal.config.config import Config

TEMPLATES_DIRECTORY = pathlib.Path("_internal", "templates")
TEMPLATE_NAME = "mbed_config.tmpl"


def generate_mbed_config_cmake_file(mbed_target_name: str, config: Config, toolchain_name: str) -> str:
    """Generate mbed_config.cmake containing the correct definitions for a build.

    Args:
        mbed_target_name: the target the application is being built for
        config: Config object holding information parsed from the mbed config system.
        toolchain_name: the toolchain to be used to build the application

    Returns:
        A string of rendered contents for the file.
    """
    return _render_mbed_config_cmake_template(config, toolchain_name, mbed_target_name,)


def _render_mbed_config_cmake_template(config: Config, toolchain_name: str, target_name: str) -> str:
    """Renders the mbed_config template with the relevant information.

    Args:
        config: Config object holding information parsed from the mbed config system.
        toolchain_name: Name of the toolchain being used.
        target_name: Name of the target.

    Returns:
        The contents of the rendered CMake file.
    """
    env = jinja2.Environment(loader=jinja2.PackageLoader("mbed_tools.build", str(TEMPLATES_DIRECTORY)),)
    template = env.get_template(TEMPLATE_NAME)
    config["supported_c_libs"] = [x for x in config["supported_c_libs"][toolchain_name.lower()]]
    context = {"target_name": target_name, "toolchain_name": toolchain_name, **config}
    return template.render(context)
