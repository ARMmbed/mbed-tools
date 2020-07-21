#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Creation and management of Mbed OS projects.

* Creation of a new Mbed OS application.
* Cloning of an existing Mbed OS program.
* Checkout of a specific version of Mbed OS or library.
"""

from mbed_tools.project.project import initialise_project, clone_project, checkout_project_revision, get_known_libs
from mbed_tools.project.mbed_program import MbedProgram
