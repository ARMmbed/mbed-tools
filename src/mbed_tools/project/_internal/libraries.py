#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Objects for library reference handling."""
import logging

from dataclasses import dataclass
from pathlib import Path
from typing import Generator, List

from mbed_tools.project._internal import git_utils

logger = logging.getLogger(__name__)


@dataclass(frozen=True, order=True)
class MbedLibReference:
    """Metadata associated with an Mbed library.

    An Mbed library is an external dependency of an MbedProgram. The MbedProgram is made aware of the library
    dependency by the presence of a .lib file in the project tree, which we refer to as a library reference file. The
    library reference file contains a URI where the dependency's source code can be fetched.

    Attributes:
        reference_file: Path to the .lib reference file for this library.
        source_code_path: Path to the source code if it exists in the local project.
    """

    reference_file: Path
    source_code_path: Path

    def is_resolved(self) -> bool:
        """Determines if the source code for this library is present in the source tree."""
        return self.source_code_path.exists() and self.source_code_path.is_dir()

    def get_git_reference(self) -> git_utils.GitReference:
        """Get the source code location from the library reference file.

        Returns:
            Data structure containing the contents of the library reference file.
        """
        raw_ref = self.reference_file.read_text().strip()
        url, sep, ref = raw_ref.partition("#")

        if url.endswith("/"):
            url = url[:-1]

        return git_utils.GitReference(repo_url=url, ref=ref)


@dataclass
class LibraryReferences:
    """Manages library references in an MbedProgram."""

    root: Path
    ignore_paths: List[str]

    def fetch(self) -> None:
        """Recursively clone all dependencies defined in .lib files."""
        for lib in self.iter_unresolved():
            git_ref = lib.get_git_reference()
            logger.info(f"Resolving library reference {git_ref.repo_url}.")
            repo = git_utils.clone(git_ref.repo_url, lib.source_code_path)
            if git_ref.ref:
                logger.info(f"Checking out revision {git_ref.ref} for library {git_ref.repo_url}.")
                git_utils.checkout(repo, git_ref.ref)

        # Check if we find any new references after cloning dependencies.
        if list(self.iter_unresolved()):
            self.fetch()

    def checkout(self, force: bool) -> None:
        """Check out all resolved libs to revision specified in .lib files."""
        for lib in self.iter_resolved():
            repo = git_utils.get_repo(lib.source_code_path)
            git_ref = lib.get_git_reference()

            if not git_ref.ref:
                repo.git.fetch()
                git_ref.ref = git_utils.get_default_branch(repo)
            else:
                # Fetch only the requested ref
                repo.git.fetch("origin", git_ref.ref)

            git_utils.checkout(repo, git_ref.ref, force=force)

    def iter_all(self) -> Generator[MbedLibReference, None, None]:
        """Iterate all library references in the tree.

        Yields:
            Iterator to library reference.
        """
        for lib in self.root.rglob("*.lib"):
            if not self._in_ignore_path(lib):
                yield MbedLibReference(lib, lib.with_suffix(""))

    def iter_unresolved(self) -> Generator[MbedLibReference, None, None]:
        """Iterate all unresolved library references in the tree.

        Yields:
            Iterator to library reference.
        """
        for lib in self.iter_all():
            if not lib.is_resolved():
                yield lib

    def iter_resolved(self) -> Generator[MbedLibReference, None, None]:
        """Iterate all resolved library references in the tree.

        Yields:
            Iterator to library reference.
        """
        for lib in self.iter_all():
            if lib.is_resolved():
                yield lib

    def _in_ignore_path(self, lib_reference_path: Path) -> bool:
        """Check if a library reference is in a path we want to ignore."""
        return any(p in lib_reference_path.parts for p in self.ignore_paths)
