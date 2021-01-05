#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Synchronise the offline target database with the online database.

This utility performs the following actions:
* Downloads the latest online target database
* Saves the database to a local file in the mbed-tools repository
* Writes a news file detailing any added, removed or modified boards
"""

import argparse
import logging
import sys

from dataclasses import dataclass
from pathlib import Path

from mbed_tools_ci_scripts.create_news_file import create_news_file, NewsType
from mbed_tools.lib.exceptions import ToolsError
from mbed_tools.lib.logging import log_exception, set_log_level

from mbed_tools.targets._internal.board_database import get_board_database_path
from mbed_tools.targets.boards import Boards

logger = logging.getLogger()

BOARD_DATABASE_PATH = get_board_database_path()


@dataclass(frozen=True)
class DatabaseComparisonResult:
    """Result of the database comparison."""

    boards_added: set
    boards_removed: set
    boards_modified: set


def save_board_database(board_database_text: str, output_file_path: Path) -> None:
    """Save a snapshot of the board database to a local file.

    Args:
        board_database_text: json formatted text containing the board data returned from the online database
        output_file_path: the path to the output file
    """
    output_file_path.parent.mkdir(exist_ok=True)
    output_file_path.write_text(board_database_text)


def compare_databases(offline_boards: Boards, online_boards: Boards) -> DatabaseComparisonResult:
    """Compare offline and online board databases."""
    added = online_boards - offline_boards
    removed = offline_boards - online_boards
    added_board_names = set(b.board_name for b in added)
    removed_board_names = set(b.board_name for b in removed)
    modified_board_names = added_board_names & removed_board_names
    added_board_names -= modified_board_names
    removed_board_names -= modified_board_names
    return DatabaseComparisonResult(added_board_names, removed_board_names, modified_board_names)


def create_news_item_text_from_boards(prefix: str, board_names: set) -> str:
    """Create a news item string from the list of boards."""
    return f"{prefix} {', '.join(sorted(board_names))}.\n"


def create_news_file_text_from_result(result: DatabaseComparisonResult) -> str:
    """Creates and writes a news file from the result of the database update.

    Args:
        result: Result of the database update
    """
    news_item_text = ""
    if result.boards_added:
        news_item_text = create_news_item_text_from_boards("Targets added:", result.boards_added)

    if result.boards_removed:
        news_item_text = create_news_item_text_from_boards(f"{news_item_text}Targets removed:", result.boards_removed)

    if result.boards_modified:
        news_item_text = create_news_item_text_from_boards(f"{news_item_text}Targets modified:", result.boards_modified)

    return news_item_text


def parse_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0)
    return parser.parse_args()


def main(args: argparse.Namespace) -> int:
    """Main entry point."""
    set_log_level(args.verbose)
    try:
        online_boards = Boards.from_online_database()
        offline_boards = Boards.from_offline_database()
        result = compare_databases(offline_boards, online_boards)
        if not (result.boards_added or result.boards_removed or result.boards_modified):
            logger.info("No changes to commit. Exiting.")
            return 0

        news_file_text = create_news_file_text_from_result(result)
        create_news_file(news_file_text, NewsType.feature)
        save_board_database(online_boards.json_dump(), BOARD_DATABASE_PATH)
        return 0
    except ToolsError as tools_error:
        log_exception(logger, tools_error)
        return 1


if __name__ == "__main__":
    sys.exit(main(parse_args()))
