"""Entry point for mbed-tools cli."""
import click


@click.command()
def cli():
    """Prints Hello."""
    click.echo("Hello.")
