#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Defines the public API of the package."""
import pathlib
import logging

from typing import Dict, Any

from mbed_tools.project.mbed_program import MbedProgram, parse_url

logger = logging.getLogger(__name__)


def clone_project(url: str, dst_path: Any = None, recursive: bool = False) -> None:
    """Clones an Mbed project from a remote repository.

    Args:
        url: URL of the repository to clone.
        dst_path: Destination path for the repository.
        recursive: Recursively clone all project dependencies.
    """
    git_data = parse_url(url)
    url = git_data["url"]
    if not dst_path:
        dst_path = pathlib.Path(git_data["dst_path"])

    program = MbedProgram.from_url(url, dst_path)
    if recursive:
        program.resolve_libraries()


def initialise_project(path: pathlib.Path, create_only: bool) -> None:
    """Create a new Mbed project, optionally fetching and adding mbed-os.

    Args:
        path: Path to the project folder. Created if it doesn't exist.
        create_only: Flag which suppreses fetching mbed-os. If the value is `False`, fetch mbed-os from the remote.
    """
    program = MbedProgram.from_new(path)
    if not create_only:
        program.resolve_libraries()


def checkout_project_revision(path: pathlib.Path, force: bool = False) -> None:
    """Checkout a specific revision of the current Mbed project.

    This function also resolves and syncs all library dependencies to the revision specified in the library reference
    files.

    Args:
        path: Path to the Mbed project.
        project_revision: Revision of the Mbed project to check out.
        force: Force overwrite uncommitted changes. If False, the checkout will fail if there are uncommitted local
               changes.
    """
    program = MbedProgram.from_existing(path, check_mbed_os=False)
    program.checkout_libraries(force=force)
    if program.has_unresolved_libraries():
        logger.info("Unresolved libraries detected, downloading library source code.")
        program.resolve_libraries()


def get_known_libs(path: pathlib.Path) -> Dict[str, Any]:
    """List all resolved library dependencies.

    This function will not resolve dependencies. This will only generate a list of resolved dependencies.

    Args:
        path: Path to the Mbed project.

    Returns:
        dictionary containing a list of known dependencies and a boolean stating whether unresolved dependencies were
        detected.
    """
    program = MbedProgram.from_existing(path, check_mbed_os=False)

    return {"known_libs": program.list_known_library_dependencies(), "unresolved": program.has_unresolved_libraries()}
