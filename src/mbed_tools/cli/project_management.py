#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Project management commands: init, clone, checkout and libs."""
import os
import pathlib

from typing import Any

import click
import tabulate

from mbed_tools.project import initialise_project, clone_project, get_known_libs, checkout_project_revision


@click.command()
@click.option("--create-only", "-c", is_flag=True, show_default=True, help="Create a program without fetching mbed-os.")
@click.argument("path", type=click.Path())
def init(path: str, create_only: bool) -> None:
    """Creates a new Mbed project at the specified path. Downloads mbed-os and adds it to the project.

    PATH: Path to the destination directory for the project. Will be created if it does not exist.
    """
    click.echo(f"Creating a new Mbed program at path '{path}'.")
    if not create_only:
        click.echo("Downloading mbed-os and adding it to the project.")

    initialise_project(pathlib.Path(path), create_only)


@click.command()
@click.argument("url")
@click.argument("path", type=click.Path(), default="")
@click.option(
    "--skip-resolve-libs",
    "-s",
    is_flag=True,
    show_default=True,
    help="Skip resolving program library dependencies after cloning.",
)
def clone(url: str, path: Any, skip_resolve_libs: bool) -> None:
    """Clone an Mbed project and library dependencies.

    URL: The git url of the remote project to clone.

    PATH: Destination path for the clone. If not given the destination path is set to the project name in the cwd.
    """
    click.echo(f"Cloning Mbed program '{url}'")
    if not skip_resolve_libs:
        click.echo("Resolving program library dependencies.")

    if path:
        click.echo(f"Destination path is '{path}'")
        path = pathlib.Path(path)

    clone_project(url, path, not skip_resolve_libs)


@click.command()
@click.argument("path", type=click.Path(), default=os.getcwd())
def libs(path: str) -> None:
    """List all resolved library dependencies.

    PATH: Path to the Mbed project [default: CWD]
    """
    lib_data = get_known_libs(pathlib.Path(path))
    click.echo("This program has the following library dependencies: \n")
    table = []
    for lib in sorted(lib_data["known_libs"]):
        table.append([lib.reference_file.stem, lib.get_git_reference().repo_url, lib.get_git_reference().ref])

    headers = ("Library Name", "Repository URL", "Git reference")
    click.echo(tabulate.tabulate(table, headers=headers))

    if lib_data["unresolved"]:
        click.echo(
            "\nUnresolved libraries detected. Please run the `checkout` command to download library source code."
        )


@click.command()
@click.argument("path", type=click.Path(), default=os.getcwd())
@click.option(
    "--force", "-f", is_flag=True, show_default=True, help="Force checkout, overwrites local uncommitted changes."
)
def checkout(path: str, force: bool) -> None:
    """Checks out Mbed program library dependencies at the revision specified in the ".lib" files.

    Ensures all dependencies are resolved and the versions are synchronised to the version specified in the library
    reference.

    PATH: Path to the Mbed project [default: CWD]

    REVISION: The revision of the Mbed project to check out.
    """
    click.echo("Checking out all libraries to revisions specified in .lib files. Resolving any unresolved libraries.")
    checkout_project_revision(pathlib.Path(path), force)
