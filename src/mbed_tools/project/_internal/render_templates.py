#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Render jinja templates required by the project package."""
import datetime
import logging

from pathlib import Path

import jinja2
import requests

logger = logging.getLogger(__name__)

TEMPLATES_DIRECTORY = Path("_internal", "templates")


def render_cmakelists_template(cmakelists_file: Path, program_name: str) -> None:
    """Render CMakeLists.tmpl with the copyright year and program name as the app target name.

    Args:
        cmakelists_file: The path where CMakeLists.txt will be written.
        program_name: The name of the program, will be used as the app target name.
    """
    context = {"program_name": program_name, "year": str(datetime.datetime.now().year)}

    try:
        cmakelists_url = "https://raw.githubusercontent.com/ARMmbed/mbed-os/master/tools/cmake/CMakeLists.tmpl"
        response = requests.get(cmakelists_url)
        response.raise_for_status()
        template = render_jinja_template_from_string(response.text, context)
    except requests.exceptions.RequestException:
        template = render_jinja_template("CMakeLists.tmpl", context)
        logger.warning("Failed to fetch a new version of the template, using a cached copy.")

    cmakelists_file.write_text(template)


def render_main_cpp_template(main_cpp: Path) -> None:
    """Render a basic main.cpp which prints a hello message and returns.

    Args:
        main_cpp: Path where the main.cpp file will be written.
    """
    main_cpp.write_text(render_jinja_template("main.tmpl", {"year": str(datetime.datetime.now().year)}))


def render_gitignore_template(gitignore: Path) -> None:
    """Write out a basic gitignore file ignoring the build and config directory.

    Args:
        gitignore: The path where the gitignore file will be written.
    """
    gitignore.write_text(render_jinja_template("gitignore.tmpl", {}))


def render_jinja_template(template_name: str, context: dict) -> str:
    """Render a jinja template.

    Args:
        template_name: The name of the template being rendered.
        context: Data to render into the jinja template.
    """
    env = jinja2.Environment(loader=jinja2.PackageLoader("mbed_tools.project", str(TEMPLATES_DIRECTORY)))
    template = env.get_template(template_name)
    return template.render(context)


def render_jinja_template_from_string(template_text: str, context: dict) -> str:
    """Render a jinja template from a specified string.

    Args:
        template_text: The template being rendered.
        context: Data to render into the jinja template.
    """
    env = jinja2.Environment(loader=jinja2.BaseLoader())
    template = env.from_string(template_text)
    return template.render(context)
