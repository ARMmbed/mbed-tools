#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Parses files found on Mbed enabled devices.

There are a number of data files stored on an mbed enabled device's USB MSD filesystem.

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
import itertools
import logging
import pathlib
import re
from typing import Optional, NamedTuple, Iterable, List


logger = logging.getLogger(__name__)


class OnlineId(NamedTuple):
    """Used to identify the target against the os.mbed.com website.

    The target type and slug are used in the URI for the board and together they can be used uniquely identify a board.

    OnlineId(target_type="platform", slug="SOME-SLUG") -> https://os.mbed.com/platforms/SOME-SLUG
    """

    target_type: str
    slug: str


def read_product_code(file_contents: str) -> Optional[str]:
    """Returns product code parsed from the file contents, None if not found."""
    regex = r"""
            (?:code|auth)=                   # attribute name
            (?P<product_code>[a-fA-F0-9]{4}) # product code
    """
    match = re.search(regex, file_contents, re.VERBOSE)
    if match:
        return match["product_code"]
    return None


def read_online_id(file_contents: str) -> Optional[OnlineId]:
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


def extract_product_code_from_htm(all_files_contents: Iterable[str]) -> Optional[str]:
    """Return first product code found in files contents, None if not found."""
    for contents in all_files_contents:
        product_code = read_product_code(contents)
        if product_code:
            return product_code
    return None


def extract_online_id_from_htm(all_files_contents: Iterable[str]) -> Optional[OnlineId]:
    """Return first online id found in files contents, None if not found."""
    for contents in all_files_contents:
        online_id = read_online_id(contents)
        if online_id:
            return online_id
    return None


def get_all_htm_files_contents(directories: Iterable[pathlib.Path]) -> List[str]:
    """Yields all htm files contents found in the list of given directories."""
    files_in_each_directory = (directory.iterdir() for directory in directories)
    all_files = itertools.chain.from_iterable(files_in_each_directory)
    return _read_htm_file_contents(all_files)


def _read_htm_file_contents(all_files: Iterable[pathlib.Path]) -> List[str]:
    htm_files_contents = []
    for file in all_files:
        if _is_htm_file(file):
            try:
                htm_files_contents.append(file.read_text())
            except OSError:
                logger.warning(f"The file '{file}' could not be read from the device, target may not be identified.")
    return htm_files_contents


def _is_htm_file(file: pathlib.Path) -> bool:
    """Checks whether the file looks like an Mbed HTM file."""
    extensions = [".htm", ".HTM"]
    return file.suffix in extensions and not file.name.startswith(".")
