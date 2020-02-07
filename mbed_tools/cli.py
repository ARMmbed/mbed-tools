"""Integration point with all sub-packages."""
import click
from mbed_devices.mbed_tools.cli import cli as mbed_devices_cli


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli() -> None:
    """Main entry point for the cli."""
    pass


cli.add_command(mbed_devices_cli, "devices")
