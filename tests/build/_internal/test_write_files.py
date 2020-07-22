#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib
import tempfile
from unittest import TestCase

from mbed_tools.build._internal.write_files import write_file
from mbed_tools.build.exceptions import InvalidExportOutputDirectory


class TestWriteFile(TestCase):
    def test_writes_content_to_file(self):
        with tempfile.TemporaryDirectory() as directory:
            content = "Some rendered content"
            export_path = pathlib.Path(directory, "output")
            file_name = "some_file.txt"

            write_file(export_path, file_name, content)

            created_file = pathlib.Path(export_path, pathlib.Path(export_path, file_name))
            self.assertEqual(created_file.read_text(), content)

    def test_output_dir_is_file(self):
        with tempfile.TemporaryDirectory() as directory:
            bad_export_dir = pathlib.Path(directory, "some_file.txt")
            bad_export_dir.touch()
            with self.assertRaises(InvalidExportOutputDirectory):
                write_file(bad_export_dir, "any_file.txt", "some contents")
