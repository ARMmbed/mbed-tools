#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Command to print information about environment variables used by the tools."""
import click
import pdoc
from typing import Iterable

from mbed_tools.targets.env import env_variables as devices_env_variables


@click.command()
def cli() -> None:
    """Prints information about environment variables of all child mbed packages."""
    click.echo(_build_output(devices_env_variables))


_OUTPUT_PREAMBLE = """These variables used by Mbed Tools can be set either directly via environment variables or
using a `.env` file containing the variable definitions as follows:

VARIABLE=value

Environment variables take precedence, meaning the values set in the file will be overriden
by any values previously set in your environment.

+---------------------------------------------------------------------------------+
| Do not upload `.env` files containing private tokens to version control! If you |
| use this package as a dependency of your project, please ensure to include the  |
| `.env` in your `.gitignore`.                                                    |
+---------------------------------------------------------------------------------+
"""


def _build_output(env_variables: Iterable[pdoc.Variable]) -> str:
    variables_outputs = [f"{v.name}\n\n{_tab_prefix(v.docstring)}" for v in env_variables]
    variables_output = "\n\n".join(variables_outputs)
    return f"{_OUTPUT_PREAMBLE}\n\n{variables_output}"


def _tab_prefix(mutiline_text: str) -> str:
    return "\n".join([f"\t{line}" for line in mutiline_text.split("\n")])
