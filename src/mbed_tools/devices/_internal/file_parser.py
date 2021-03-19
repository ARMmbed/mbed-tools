#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Parses files found on Mbed enabled devices.

There are a number of data files stored on an mbed enabled device's USB mass storage.

The schema and content of these files are described in detail below.

- MBED.HTM File
We support many flavours of MBED.HTM files. The list of examples below is not exhaustive.

    <!-- mbed Microcontroller Website and Authentication Shortcut -->
    <!-- Version: 0200 Build: Feb  3 2014 14:03:10 -->
    <html>
    <head>
    <meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code=0710020092566DA9AD33FB84"/>
    <title>mbed Website Shortcut</title>
    </head>
    <body></body>
    </html>

---

    <!doctype html>
    <!-- mbed Platform Website and Authentication Shortcut -->
    <html>
    <head>
    <meta charset="utf-8">
    <title>mbed Website Shortcut</title>
    </head>
    <body>
    <script>
    window.location.replace("https://mbed.org/device/?code=460000000988254a00000000000000000000000097969902?version=0253?target_id=00000000000000000000000000000000");
    </script>
    </body>
    </html>

---

    <!-- mbed Microcontroller Website and Authentication Shortcut -->
    <html>
    <head>
    <meta http-equiv="refresh" content="0; url=http://mbed.org/start?auth=101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9&loader=11972&firmware=16457&configuration=4" />  # noqa
    <title>mbed Website Shortcut</title>
    </head>
    <body></body>
    </html>

---

    <!doctype html>
    <!-- mbed Platform Website and Authentication Shortcut -->
    <html>
    <head>
    <meta charset="utf-8">
    <title>mbed Website Shortcut</title>
    </head>
    <body>
    <script>
    window.location.replace("https://os.mbed.com/platforms/LPCXpresso54114/");
    </script>
    </body>
    </html>

"""
import logging
import pathlib
import re

from dataclasses import dataclass
from typing import Optional, NamedTuple, Iterable, List


logger = logging.getLogger(__name__)


class OnlineId(NamedTuple):
    """Used to identify the target against the os.mbed.com website.

    The target type and slug are used in the URI for the board and together they can be used uniquely identify a board.

    OnlineId(target_type="platform", slug="SOME-SLUG") -> https://os.mbed.com/platforms/SOME-SLUG
    """

    target_type: str
    slug: str


@dataclass
class DeviceFileInfo:
    """Information gathered from Mbed device files."""

    product_code: Optional[str]
    online_id: Optional[OnlineId]


def read_device_files(directory_paths: Iterable[pathlib.Path]) -> DeviceFileInfo:
    """Read data from files contained on an mbed enabled device's USB mass storage device.

    If details.txt exists and it contains a product code, then we will use that code. If not then we try to grep the
    code from the mbed.htm file. We extract an OnlineID from mbed.htm as we also make use of that information to find a
    board entry in Mbed OS's various target databases and JSON files.

    Args:
        directory_paths: Paths to the directories containing device files.
    """
    device_file_paths = _get_device_file_paths(directory_paths)
    if not device_file_paths:
        paths = "\n".join(str(p) for p in directory_paths)
        logger.warning(
            f"No files were found in the device's mass storage device. The following paths were searched:\n{paths}."
            "\nThis device may not be identifiable as Mbed enabled. Check the files exist, are not hidden and are not "
            "corrupted."
        )
        return DeviceFileInfo(None, None)

    htm_file_contents = _read_htm_file_contents(device_file_paths)
    code = _extract_product_code_from_htm(htm_file_contents)
    online_id = _extract_online_id_from_htm(htm_file_contents)
    return DeviceFileInfo(code, online_id)


def _read_product_code(file_contents: str) -> Optional[str]:
    """Returns product code parsed from the file contents, None if not found."""
    regex = r"""
            (?:code|auth)=                   # attribute name
            (?P<product_code>[a-fA-F0-9]{4}) # product code
    """
    match = re.search(regex, file_contents, re.VERBOSE)
    if match:
        return match["product_code"]
    return None


def _read_online_id(file_contents: str) -> Optional[OnlineId]:
    """Returns online id parsed from the files contents, None if not found."""
    regex = r"""
            (?P<target_type>module|platform)s   # module|platform
            \/                                  # forward slash in the url
            (?P<slug>[-\w]+)                    # permitted characters in a slug are letters and digits
    """
    match = re.search(regex, file_contents, re.VERBOSE)
    if match:
        return OnlineId(target_type=match["target_type"], slug=match["slug"])
    return None


def _extract_product_code_from_htm(all_files_contents: Iterable[str]) -> Optional[str]:
    """Return first product code found in files contents, None if not found."""
    for contents in all_files_contents:
        product_code = _read_product_code(contents)
        if product_code:
            return product_code
    return None


def _extract_online_id_from_htm(all_files_contents: Iterable[str]) -> Optional[OnlineId]:
    """Return first online ID found in files contents, None if not found."""
    for contents in all_files_contents:
        online_id = _read_online_id(contents)
        if online_id:
            return online_id
    return None


def _get_device_file_paths(directories: Iterable[pathlib.Path]) -> List[pathlib.Path]:
    return [path for directory in directories for path in directory.iterdir() if not _is_hidden_file(path)]


def _try_read_file_text(file_path: pathlib.Path) -> Optional[str]:
    try:
        return file_path.read_text()
    except OSError:
        logger.warning(f"The file '{file_path}' could not be read from the device, target may not be identified.")
        return None


def _read_htm_file_contents(all_files: Iterable[pathlib.Path]) -> List[str]:
    htm_files_contents = []
    for file in all_files:
        if _is_htm_file(file):
            contents = _try_read_file_text(file)
            if contents:
                htm_files_contents.append(contents)
    return htm_files_contents


def _is_hidden_file(file: pathlib.Path) -> bool:
    """Checks if the file is hidden."""
    return file.name.startswith(".")


def _is_htm_file(path: pathlib.Path) -> bool:
    return path.suffix.lower() == ".htm"
