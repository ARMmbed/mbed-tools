#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Facilitates parsing MBED.HTM files found on the Mbed devices.

For legacy reasons, we support many flavours of MBED.HTM files. The list of examples below is not exhaustive,
as at the time of writing it's not feasible to gather all examples in one place.
Its main goal is to provide a taste of different flavours of HTM files we need to support.

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
import re
from typing import Optional, NamedTuple


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
