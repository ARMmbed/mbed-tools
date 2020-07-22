#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Integration with https://github.com/ARMmbed/mbed-tools."""
import pdoc
from mbed_tools.targets.env import Env

env_variables = pdoc.Class("Env", pdoc.Module("mbed_tools.targets.env"), Env).instance_variables()
