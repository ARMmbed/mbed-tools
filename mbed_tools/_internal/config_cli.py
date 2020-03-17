"""Exposes a click command which prints information about configuration options of all child mbed packages.

TODO: describe the common interface of exposing configuration options by child packages
"""
import click
from tabulate import tabulate

from mbed_devices.mbed_tools import config as mbed_devices_config


@click.command()
def cli():
    """Prints information about configuration options of all child mbed packages."""
    click.echo(_build_output(_gather_configuration_options()))


def _gather_configuration_options():
    return mbed_devices_config()


_OUTPUT_PREAMBLE = """
All the configuration options can be set either via environment variables or
using a `.env` file containing the variable definitions as follows:

VARIABLE=value

The `.env` file takes precendence, meaning the values set in the file will
override any values previously set in your environment.

+---------------------------------------------------------------------------------+
| Do not upload `.env` files containing private tokens to version control! If you |
| use this package as a dependency of your project, please ensure to include the  |
| `.env` in your `.gitignore`.                                                    |
+---------------------------------------------------------------------------------+
"""


def _build_output(configuration_options):
    options_table = tabulate(
        [[option.name, option.doc] for option in configuration_options], headers=["Name", "Description"]
    )
    return f"{_OUTPUT_PREAMBLE}\n{options_table}"
