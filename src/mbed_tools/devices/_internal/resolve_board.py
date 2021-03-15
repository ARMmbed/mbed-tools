#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Resolve targets for `CandidateDevice`.

Resolving a target involves looking up an `MbedTarget` from the `mbed-targets` API, using data found in the "htm file"
located on an "Mbed Enabled" device's USB MSD.

For more information on the mbed-targets package visit https://github.com/ARMmbed/mbed-targets
"""
import logging

from mbed_tools.targets import Board, get_board_by_product_code, get_board_by_online_id
from mbed_tools.targets.exceptions import UnknownBoard

from mbed_tools.devices._internal.file_parser import (
    extract_product_code_from_htm,
    extract_online_id_from_htm,
    get_all_htm_files_contents,
)
from mbed_tools.devices._internal.candidate_device import CandidateDevice
from mbed_tools.devices._internal.exceptions import NoBoardForCandidate


logger = logging.getLogger(__name__)


def resolve_board(candidate: CandidateDevice) -> Board:
    """Resolves board for a given CandidateDevice.

    This function interrogates CandidateDevice, attempting to establish the best method to resolve a Board,
    the rules are as follows:

    1. Use product code retrieved from one of HTM files in the mass storage if available.
    2. Use online id retrieved from one of the HTM files in the mass storage if available.
    3. Fallback to product code retrieved from serial number.

    The specification of HTM files is that they redirect to board's product page on os.mbed.com.
    Information about Mbed Enabled requirements: https://www.mbed.com/en/about-mbed/mbed-enabled/requirements/
    """
    all_files_contents = get_all_htm_files_contents(candidate.mount_points)

    product_code = extract_product_code_from_htm(all_files_contents)
    if product_code:
        try:
            return get_board_by_product_code(product_code)
        except UnknownBoard:
            logger.error(f"Could not identify a board with the product code: '{product_code}'.")
            raise NoBoardForCandidate

    online_id = extract_online_id_from_htm(all_files_contents)
    if online_id:
        slug = online_id.slug
        target_type = online_id.target_type
        try:
            return get_board_by_online_id(slug=slug, target_type=target_type)
        except UnknownBoard:
            logger.error(f"Could not identify a board with the slug: '{slug}' and target type: '{target_type}'.")
            raise NoBoardForCandidate

    # Product code might be the first 4 characters of the serial number
    try:
        product_code = candidate.serial_number[:4]
        return get_board_by_product_code(product_code)
    except UnknownBoard:
        # Most devices have a serial number so this may not be a problem
        logger.info(
            f"The device with the Serial Number: '{candidate.serial_number}' (Product Code: '{product_code}') "
            f"does not appear to be an Mbed development board."
        )
        raise NoBoardForCandidate
