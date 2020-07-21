#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Objects representing Mbed program and library data."""
import json
import logging

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# mbed program file names and constants.
TARGETS_JSON_FILE_PATH = Path("targets", "targets.json")
MBED_OS_DIR_NAME = "mbed-os"
MBED_OS_REFERENCE_URL = "https://github.com/ARMmbed/mbed-os"
MBED_OS_REFERENCE_FILE_NAME = "mbed-os.lib"
PROGRAM_ROOT_FILE_NAME = ".mbed"
APP_CONFIG_FILE_NAME = "mbed_app.json"


# For some reason Mbed OS expects the default mbed_app.json to contain some target_overrides
# for the K64F target. TODO: Find out why this wouldn't be defined in targets.json.
DEFAULT_APP_CONFIG = {"target_overrides": {"K64F": {"platform.stdio-baud-rate": 9600}}}


@dataclass
class MbedProgramFiles:
    """Files defining an MbedProgram.

    This object holds paths to the various files which define an MbedProgram.

    All MbedPrograms must contain a .mbed file, which defines the program root path. MbedPrograms must also contain an
    mbed-os.lib reference file, defining Mbed OS as a program dependency. Because the mbed-os.lib reference is required
    by all Mbed programs the path to the file is stored in this object.

    Attributes:
        app_config_file: Path to mbed_app.json file. This can be `None` if the program doesn't set any custom config.
        mbed_file: Path to the .mbed file which defines the program root.
        mbed_os_ref: Library reference file for MbedOS. All programs require this file.
    """

    app_config_file: Optional[Path]
    mbed_file: Path
    mbed_os_ref: Path

    @classmethod
    def from_new(cls, root_path: Path) -> "MbedProgramFiles":
        """Create MbedProgramFiles from a new directory.

        A "new directory" in this context means it doesn't already contain an Mbed program.

        Args:
            root_path: The directory in which to create the program data files.

        Raises:
            ValueError: A program .mbed or mbed-os.lib file already exists at this path.
        """
        app_config = root_path / APP_CONFIG_FILE_NAME
        mbed_file = root_path / PROGRAM_ROOT_FILE_NAME
        mbed_os_ref = root_path / MBED_OS_REFERENCE_FILE_NAME

        if mbed_file.exists() or mbed_os_ref.exists():
            raise ValueError(f"Program already exists at path {root_path}.")

        mbed_file.touch()
        app_config.write_text(json.dumps(DEFAULT_APP_CONFIG, indent=4))
        mbed_os_ref.write_text(f"{MBED_OS_REFERENCE_URL}#master")
        return cls(app_config_file=app_config, mbed_file=mbed_file, mbed_os_ref=mbed_os_ref)

    @classmethod
    def from_existing(cls, root_path: Path) -> "MbedProgramFiles":
        """Create MbedProgramFiles from a directory containing an existing program.

        Args:
            root_path: The path containing the MbedProgramFiles.

        Raises:
            ValueError: no MbedProgramFiles exists at this path.
        """
        app_config: Optional[Path]
        app_config = root_path / APP_CONFIG_FILE_NAME
        if not app_config.exists():
            logger.info("This program does not contain an mbed_app.json config file.")
            app_config = None

        mbed_os_file = root_path / MBED_OS_REFERENCE_FILE_NAME
        if not mbed_os_file.exists():
            raise ValueError("This path does not contain an mbed-os.lib, which is required for mbed programs.")

        mbed_file = root_path / PROGRAM_ROOT_FILE_NAME
        mbed_file.touch(exist_ok=True)

        return cls(app_config_file=app_config, mbed_file=mbed_file, mbed_os_ref=mbed_os_file)


@dataclass
class MbedOS:
    """Metadata associated with a copy of MbedOS.

    This object holds information about MbedOS used by MbedProgram.

    Attributes:
        root: The root path of the MbedOS source tree.
        targets_json_file: Path to a targets.json file, which contains target data specific to MbedOS revision.
    """

    root: Path
    targets_json_file: Path

    @classmethod
    def from_existing(cls, root_path: Path, check_root_path_exists: bool = True) -> "MbedOS":
        """Create MbedOS from a directory containing an existing MbedOS installation."""
        targets_json_file = root_path / TARGETS_JSON_FILE_PATH

        if check_root_path_exists and not root_path.exists():
            raise ValueError("The mbed-os directory does not exist.")

        if root_path.exists() and not targets_json_file.exists():
            raise ValueError("This MbedOS copy does not contain a targets.json file.")

        return cls(root=root_path, targets_json_file=targets_json_file)

    @classmethod
    def from_new(cls, root_path: Path) -> "MbedOS":
        """Create MbedOS from an empty or new directory."""
        return cls(root=root_path, targets_json_file=root_path / TARGETS_JSON_FILE_PATH)
