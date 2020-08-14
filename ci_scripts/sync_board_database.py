#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Synchronise the offline target database with the online database.

This utility performs the following actions:
* Downloads the latest online target database
* Saves the database to a local file in the mbed-targets repository
* Creates a new branch and commits the new target database
* Pushes the branch to the mbed-targets remote and raises a github PR as Monty Bot.
"""

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, List

from github import Github, GithubException

from mbed_tools_ci_scripts.create_news_file import create_news_file, NewsType
from mbed_tools_ci_scripts.utils import git_helpers
from mbed_tools_ci_scripts.utils.configuration import configuration, ConfigurationVariable
from mbed_tools.lib.exceptions import ToolsError
from mbed_tools.lib.logging import log_exception, set_log_level

from mbed_tools.targets._internal.board_database import get_board_database_path
from mbed_tools.targets.boards import Boards

logger = logging.getLogger()

BOARD_DATABASE_PATH = get_board_database_path()


class PullRequestInfo(NamedTuple):
    """Data structure containing info required to raise a Github PR."""

    repo: str
    head_branch: str
    base_branch: str
    subject: str
    body: str


@dataclass(frozen=True)
class DatabaseUpdateResult:
    """Object containing the result of the database update."""

    boards_added: set
    boards_removed: set


def save_board_database(board_database_text: str, output_file_path: Path) -> None:
    """Save a snapshot of the board database to a local file.

    Args:
        board_database_text: json formatted text containing the board data returned from the online database
        output_file_path: the path to the output file
    """
    output_file_path.parent.mkdir(exist_ok=True)
    output_file_path.write_text(board_database_text)


def determine_board_database_update_result(offline_boards: Boards, online_boards: Boards) -> DatabaseUpdateResult:
    """Check boards added and removed in relation to the offline board database."""
    added = online_boards - offline_boards
    removed = offline_boards - online_boards
    return DatabaseUpdateResult(added, removed)


def create_news_item_text_from_boards(prefix: str, boards: Boards) -> str:
    """Create a news item string from the list of boards."""
    board_names = ", ".join(board.board_name for board in boards)
    return f"{prefix} {board_names}.\n"


def create_news_file_text_from_result(result: DatabaseUpdateResult) -> str:
    """Creates and writes a news file from the result of the database update.

    Args:
        result: Result of the database update
    """
    news_item_text = ""
    if result.boards_added:
        news_item_text = create_news_item_text_from_boards("Targets added:", result.boards_added)

    if result.boards_removed:
        news_item_text = create_news_item_text_from_boards(f"{news_item_text}Targets removed:", result.boards_removed)

    return news_item_text


def git_commit_and_push(files_to_commit: List[Path], branch_name: str, commit_msg: str) -> None:
    """Commit a file to the git remote, on a new branch, as Monty Bot.

    If the given branch doesn't exist then a new branch will be created.

    Args:
        files_to_commit: list of paths to the files to commit.
        branch_name: branch to add the commit to.
        commit_msg: the commit message.
    """
    logger.info(f"Committing '{files_to_commit}' to branch '{branch_name}' with commit message '{commit_msg}'.")
    with git_helpers.ProjectTempClone("master") as temp_clone:
        temp_clone.configure_for_github()
        temp_clone.fetch()
        temp_clone.create_branch(branch_name)
        temp_clone.checkout_branch(branch_name)
        temp_clone.add(files_to_commit)
        temp_clone.commit(commit_msg)
        temp_clone.pull()
        temp_clone.push()


def raise_github_pr(pr_info: PullRequestInfo) -> None:
    """Raise a PR on github using the GIT_TOKEN environment variable to authenticate.

    Args:
        pr_info: data structure containing information about the PR to raise.
    """
    logger.info(f"Raising PR {pr_info!r}")
    git_token = configuration.get_value(ConfigurationVariable.GIT_TOKEN)
    github_instance = Github(git_token)
    repo = github_instance.get_repo(pr_info.repo)
    try:
        repo.create_pull(title=pr_info.subject, body=pr_info.body, head=pr_info.head_branch, base=pr_info.base_branch)
    except GithubException as err:
        logging.info(err.data["errors"][0]["message"])


def parse_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.add_argument("--head-branch", default="sync-target-db")
    parser.add_argument("--base-branch", default="master")
    parser.add_argument("--pr-subject", default="Update target database.")
    parser.add_argument("--pr-description", default="")
    return parser.parse_args()


def main(args: argparse.Namespace) -> int:
    """Main entry point."""
    set_log_level(args.verbose)
    pr_info = PullRequestInfo(
        repo="ARMMbed/mbed-targets",
        head_branch=args.head_branch,
        base_branch=args.base_branch,
        subject=args.pr_subject,
        body=args.pr_description,
    )
    try:
        online_boards = Boards.from_online_database()
        if BOARD_DATABASE_PATH.exists():
            offline_boards = Boards.from_offline_database()
            result = determine_board_database_update_result(offline_boards, online_boards)
            if not (result.boards_added or result.boards_removed):
                logger.info("No changes to commit. Exiting.")
                return 0

            news_file_text = create_news_file_text_from_result(result)
        else:
            news_file_text = "Offline board database created."

        news_file_path = create_news_file(news_file_text, NewsType.feature)
        save_board_database(online_boards.json_dump(), BOARD_DATABASE_PATH)
        git_commit_and_push([BOARD_DATABASE_PATH, news_file_path], pr_info.head_branch, pr_info.subject)
        raise_github_pr(pr_info)
        return 0
    except ToolsError as tools_error:
        log_exception(logger, tools_error)
        return 1


if __name__ == "__main__":
    sys.exit(main(parse_args()))
