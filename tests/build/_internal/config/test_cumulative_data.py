#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from dataclasses import fields
from unittest import TestCase

from mbed_tools.build._internal.config.cumulative_data import CumulativeData
from tests.build._internal.config.factories import SourceFactory


class TestCumulativeDataFromSources(TestCase):
    def test_assembles_metadata_from_sources(self):
        for field in fields(CumulativeData):
            with self.subTest(f"Assemble {field.name}"):
                source_a = SourceFactory(overrides={f"target.{field.name}": ["FOO"]})
                source_b = SourceFactory(overrides={f"target.{field.name}_add": ["BAR", "BAZ"]})
                source_c = SourceFactory(overrides={f"target.{field.name}_remove": ["BAR"]})

                config_cumulative_data = CumulativeData.from_sources([source_a, source_b, source_c])

                self.assertEqual(getattr(config_cumulative_data, field.name), {"FOO", "BAZ"})
