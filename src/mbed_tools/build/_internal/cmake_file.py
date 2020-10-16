#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Module in charge of CMake file generation."""
import pathlib
from typing import Iterable

import jinja2

from mbed_tools.build._internal.config.config import Config

TEMPLATES_DIRECTORY = pathlib.Path("_internal", "templates")
TEMPLATE_NAME = "mbed_config.tmpl"


def generate_mbed_config_cmake_file(
    mbed_target_name: str, target_build_attributes: dict, config: Config, toolchain_name: str
) -> str:
    """Generate the top-level CMakeLists.txt file containing the correct definitions for a build.

    Args:
        mbed_target: the target the application is being built for
        target_build_attributes: map of target attributes
        program_path: the path to the local Mbed program
        toolchain_name: the toolchain to be used to build the application

    Returns:
        A string of rendered contents for the file.
    """
    return _render_mbed_config_cmake_template(target_build_attributes, config, toolchain_name, mbed_target_name,)


def _render_mbed_config_cmake_template(
    target_build_attributes: dict, config: Config, toolchain_name: str, target_name: str
) -> str:
    """Renders the mbed_config template with the relevant information.

    Args:
        target_build_attributes: Target config object.
        config: Config object holding information parsed from the mbed config system.
        toolchain_name: Name of the toolchain being used.
        target_name: Name of the target.

    Returns:
        The contents of the rendered CMake file.
    """
    env = jinja2.Environment(loader=jinja2.PackageLoader("mbed_tools.build", str(TEMPLATES_DIRECTORY)),)
    template = env.get_template(TEMPLATE_NAME)
    options = list(config.options.values())
    macros = list(config.macros.values())
    supported_c_libs = [x for x in target_build_attributes["supported_c_libs"][toolchain_name.lower()]]

    context = {
        "labels": target_build_attributes["labels"],
        "extra_labels": target_build_attributes["extra_labels"],
        "features": target_build_attributes["features"],
        "components": target_build_attributes["components"],
        "device_has": target_build_attributes["device_has"],
        "target_macros": target_build_attributes["macros"],
        "supported_form_factors": target_build_attributes["supported_form_factors"],
        "supported_c_libs": supported_c_libs,
        "supported_application_profiles": target_build_attributes["supported_application_profiles"],
        "c_lib": target_build_attributes["c_lib"],
        "core": target_build_attributes["core"],
        "printf_lib": target_build_attributes["printf_lib"],
        "target_name": target_name,
        "toolchain_name": toolchain_name,
        "options": sorted(options, key=lambda option: option.macro_name),
        "macros": sorted(macros, key=lambda macro: macro.name),
        "max_name_length": max(_max_attribute_length(options, "macro_name"), _max_attribute_length(macros, "name")),
        "max_value_length": max(_max_attribute_length(options, "value"), _max_attribute_length(macros, "value")),
    }
    return template.render(context)


def _max_attribute_length(objects: Iterable[object], attribute: str) -> int:
    attrs = (getattr(o, attribute) for o in objects)
    try:
        return max(len(str(attr)) for attr in attrs if attr is not None)
    except ValueError:  # no attrs found
        return 0
