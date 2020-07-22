#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Public exceptions raised by the package."""
from mbed_tools.lib.exceptions import ToolsError


class MbedBuildError(ToolsError):
    """Base public exception for the mbed-build package."""


class InvalidExportOutputDirectory(MbedBuildError):
    """It is not possible to export to the provided output directory."""
