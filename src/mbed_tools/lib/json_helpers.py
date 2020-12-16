#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Helpers for json related functions."""
import json
import logging

from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def decode_json_file(path: Path) -> Any:
    """Return the contents of json file."""
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON data in the file located at '{path}'")
        raise
