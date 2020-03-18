"""Exposes a click command which prints information about configuration variables of all child mbed packages."""
import click
import pdoc
from typing import Iterable


from mbed_devices.mbed_tools import config_variables as mbed_devices_config_variables


@click.command()
def cli() -> None:
    """Prints information about configuration variables of all child mbed packages."""
    click.echo(_build_output(mbed_devices_config_variables))


_OUTPUT_PREAMBLE = """All the configuration variables can be set either via environment variables or
using a `.env` file containing the variable definitions as follows:

VARIABLE=value

Environment variables take precendence, meaning the values set in the file will be overriden
by any values previously set in your environment.

+---------------------------------------------------------------------------------+
| Do not upload `.env` files containing private tokens to version control! If you |
| use this package as a dependency of your project, please ensure to include the  |
| `.env` in your `.gitignore`.                                                    |
+---------------------------------------------------------------------------------+
"""


def _build_output(config_variables: Iterable[pdoc.Variable]) -> str:
    variables_outputs = [f"{v.name}\n\n{_tab_prefix(v.docstring)}" for v in config_variables]
    variables_output = "\n\n".join(variables_outputs)
    return f"{_OUTPUT_PREAMBLE}\n\n{variables_output}"


def _tab_prefix(mutiline_text: str) -> str:
    return "\n".join([f"\t{line}" for line in mutiline_text.split("\n")])
