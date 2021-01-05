#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from mbed_tools.project._internal.render_templates import (
    render_cmakelists_template,
    render_main_cpp_template,
    render_gitignore_template,
)


@mock.patch("mbed_tools.project._internal.render_templates.datetime")
class TestRenderTemplates(TestCase):
    def test_renders_cmakelists_template(self, mock_datetime):
        with TemporaryDirectory() as tmpdir:
            the_year = 3999
            mock_datetime.datetime.now.return_value.year = the_year
            program_name = "mytestprogram"
            file_path = Path(tmpdir, "mytestpath")

            render_cmakelists_template(file_path, program_name)

            output = file_path.read_text()
            self.assertIn(str(the_year), output)
            self.assertIn(program_name, output)

    def test_renders_main_cpp_template(self, mock_datetime):
        with TemporaryDirectory() as tmpdir:
            the_year = 3999
            mock_datetime.datetime.now.return_value.year = the_year
            file_path = Path(tmpdir, "mytestpath")

            render_main_cpp_template(file_path)

            self.assertIn(str(the_year), file_path.read_text())

    def test_renders_gitignore_template(self, _):
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir, "mytestpath")

            render_gitignore_template(file_path)

            self.assertIn("cmake_build", file_path.read_text())
            self.assertIn(".mbedbuild", file_path.read_text())
