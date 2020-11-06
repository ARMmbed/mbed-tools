#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tag a new version based on the presence of news fragments.

mbed-tools follows a semantic versioning scheme based on the extension of the news file added to a commit.

The following versioning scheme is used:

    Extension  | Version Bumped
    ---------------------------
     .major    | Major version
     .feature  | Minor version
     .bugfix   | Patch version
     .doc      | N/A
     .removal  | N/A
     .misc     | N/A

This script will look at the latest tag reachable from the current commit using `git describe`, it will then look in
the news fragments directory, passed on the command line, and deduce which part of the version needs to be bumped based
on the news file extension.
"""
import argparse
import logging
import pathlib
import sys

import git
import semver

from typing import Iterable, Tuple


def bump_version_from_news_files(current_version: str, news_files: Iterable[pathlib.Path]) -> str:
    """Bumps the current version based on the given list of news files.

    Looks at the list of news files, determines which part of the version to bump based on the extension.

    Args:
        current_version: The current version. Does not accept all pep440 version strings.
        news_files: Iterable of news files used to work out which part of the current_version to bump.

    Returns:
        The new version as a semver formatted string.
    """
    semver_to_bump = news_ext_to_version_type(tuple(news.suffix for news in news_files if news.suffix != ".md"))
    version_info = semver.VersionInfo.parse(current_version)
    if semver_to_bump == "major":
        logging.info("Bumping major version.")
        version_info = version_info.bump_major()
    elif semver_to_bump == "minor":
        logging.info("Bumping minor version.")
        version_info = version_info.bump_minor()
    elif semver_to_bump == "patch":
        logging.info("Bumping patch version.")
        version_info = version_info.bump_patch()

    new_version = f"{version_info.major}.{version_info.minor}.{version_info.patch}"
    logging.info("New version is: %s", new_version)
    return new_version


def news_ext_to_version_type(news_file_exts: Tuple[str]) -> str:
    """Given a tuple of news file extensions, work out which part of the version to bump.

    Args:
        news_file_exts: The news file extensions to be considered.

    Returns:
        The part of the version to bump as a string.
    """
    logging.debug("News file extensions found: %s", set(news_file_exts))
    if ".major" in news_file_exts:
        return "major"
    elif ".feature" in news_file_exts:
        return "minor"
    elif ".bugfix" in news_file_exts:
        return "patch"
    raise ValueError("No significant news file extensions found. Version will not be incremented.")


def parse_args() -> argparse.Namespace:
    """Define the command line argument parser.

    Returns:
        argparse.Namespace containing references to the values of known command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--news-file-directory", type=pathlib.Path, required=True, help="Directory where news files are located."
    )
    parser.add_argument("-v", "--verbosity", action="count", default=0, help="Set verbosity level.")
    return parser.parse_args()


def set_log_level(verbosity: int) -> None:
    """Set the log level based on the verbosity.

    The log level is set as follows:
    verbosity = 0 -> logging.ERROR
    verbosity = 1 -> logging.WARN
    verbosity = 2 -> logging.INFO
    verbosity = 3 -> logging.DEBUG
    """
    levels = (logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG)
    logging.getLogger().setLevel(levels[min(verbosity, len(levels) - 1)])


def get_current_version():
    """Get the current version using git describe to check the latest tag."""
    with git.Repo() as repo:
        return repo.git.describe("--tags")


def main(args: argparse.Namespace) -> int:
    """Entry point.

    Args:
        args: Parsed command line arguments.
    """
    try:
        set_log_level(args.verbosity)
        current_version = get_current_version()
        logging.info("Current version is %s", current_version)
        new_version = bump_version_from_news_files(current_version, list(args.news_file_directory.iterdir()))
        print(new_version)
        return 0
    except Exception as e:
        logging.error(e)
        return 1


if __name__ == "__main__":
    sys.exit(main(parse_args()))
