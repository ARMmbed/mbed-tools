#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from dataclasses import fields
from unittest import TestCase

from mbed_tools.build._internal.config.bootloader_overrides import BootloaderOverrides, BootloaderOverride
from tests.build._internal.config.factories import SourceFactory


class TestCumulativeDataFromSources(TestCase):
    def test_assembles_metadata_from_sources(self):
        for field in fields(BootloaderOverrides):
            with self.subTest(f"Assemble {field.name}"):
                source = SourceFactory(overrides={f"target.{field.name}": ["FOO"]})

                bootloader_overrides = BootloaderOverrides.from_sources([source])

                self.assertEqual(
                    getattr(bootloader_overrides, field.name),
                    BootloaderOverride(set_by=source.human_name, name=field.name, value=["FOO"]),
                )
