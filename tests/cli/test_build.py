#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import contextlib
import os
import pathlib

from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from click.testing import CliRunner

from mbed_tools.cli.build import build
from mbed_tools.project._internal.project_data import CMAKE_CONFIG_FILE_PATH, CMAKE_BUILD_DIR


@contextlib.contextmanager
def mock_project_directory(program, mbed_config_exists=False, build_tree_exists=False):
    with TemporaryDirectory() as tmp_dir:
        root = pathlib.Path(tmp_dir, "test-project")
        root.mkdir()
        program.root = root
        program.files.cmake_build_dir = root / CMAKE_BUILD_DIR
        program.files.cmake_config_file = root / CMAKE_CONFIG_FILE_PATH
        if mbed_config_exists:
            program.files.cmake_config_file.parent.mkdir(exist_ok=True)
            program.files.cmake_config_file.touch(exist_ok=True)

        if build_tree_exists:
            program.files.cmake_build_dir.mkdir(exist_ok=True)

        yield


@mock.patch("mbed_tools.cli.build.generate_build_system")
@mock.patch("mbed_tools.cli.build.build_project")
@mock.patch("mbed_tools.cli.build.MbedProgram")
@mock.patch("mbed_tools.cli.build.generate_config")
class TestBuildCommand(TestCase):
    def test_searches_for_mbed_program_at_default_project_path(
        self, generate_config, mbed_program, build_project, generate_build_system
    ):
        runner = CliRunner()
        runner.invoke(build)

        mbed_program.from_existing.assert_called_once_with(pathlib.Path(os.getcwd()))

    def test_searches_for_mbed_program_at_user_defined_project_root(
        self, generate_config, mbed_program, build_project, generate_build_system
    ):
        project_path = "my-blinky"

        runner = CliRunner()
        runner.invoke(build, ["-p", project_path])

        mbed_program.from_existing.assert_called_once_with(pathlib.Path(project_path))

    def test_calls_generate_build_system_if_build_tree_nonexistent(
        self, generate_config, mbed_program, build_project, generate_build_system
    ):
        program = mbed_program.from_existing()
        with mock_project_directory(program, mbed_config_exists=True, build_tree_exists=False):
            runner = CliRunner()
            runner.invoke(build, ["-m", "k64f", "-t", "gcc_arm"])

            generate_build_system.assert_called_once_with(program.root, program.files.cmake_build_dir, "develop")

    def test_generate_build_system_not_called_if_build_tree_exists(
        self, generate_config, mbed_program, build_project, generate_build_system
    ):
        program = mbed_program.from_existing()
        with mock_project_directory(program, mbed_config_exists=True, build_tree_exists=True):
            runner = CliRunner()
            runner.invoke(build)

            generate_build_system.assert_not_called()

    def test_generate_config_called_if_config_script_nonexistent(
        self, generate_config, mbed_program, build_project, generate_build_system
    ):
        program = mbed_program.from_existing()
        with mock_project_directory(program, mbed_config_exists=False):
            target = "k64f"
            toolchain = "gcc_arm"

            runner = CliRunner()
            runner.invoke(build, ["-t", toolchain, "-m", target])

            generate_config.assert_called_once_with(target.upper(), toolchain.upper(), program)

    def test_raises_if_gen_config_toolchain_not_passed_when_required(
        self, generate_config, mbed_program, build_project, generate_build_system
    ):
        program = mbed_program.from_existing()
        with mock_project_directory(program, mbed_config_exists=False):
            target = "k64f"

            runner = CliRunner()
            result = runner.invoke(build, ["-m", target])

            self.assertIsNotNone(result.exception)
            self.assertRegex(result.output, "--toolchain")

    def test_raises_if_gen_config_target_not_passed_when_required(
        self, generate_config, mbed_program, build_project, generate_build_system
    ):
        program = mbed_program.from_existing()
        with mock_project_directory(program, mbed_config_exists=False):
            toolchain = "gcc_arm"

            runner = CliRunner()
            result = runner.invoke(build, ["-t", toolchain])

            self.assertIsNotNone(result.exception)
            self.assertRegex(result.output, "--mbed-target")

    def test_build_system_regenerated_when_target_and_toolchain_passed(
        self, generate_config, mbed_program, build_project, generate_build_system
    ):
        program = mbed_program.from_existing()
        with mock_project_directory(program, mbed_config_exists=True, build_tree_exists=True):
            toolchain = "gcc_arm"
            target = "k64f"

            runner = CliRunner()
            runner.invoke(build, ["-t", toolchain, "-m", target])

            generate_config.assert_called_once_with(target.upper(), toolchain.upper(), program)
            generate_build_system.assert_called_once_with(program.root, program.files.cmake_build_dir, "develop")

    def test_build_folder_removed_when_clean_flag_passed(
        self, generate_config, mbed_program, build_project, generate_build_system
    ):
        program = mbed_program.from_existing()
        with mock_project_directory(program, mbed_config_exists=True, build_tree_exists=True):
            toolchain = "gcc_arm"
            target = "k64f"

            runner = CliRunner()
            runner.invoke(build, ["-t", toolchain, "-m", target, "-c"])

            generate_config.assert_called_once_with(target.upper(), toolchain.upper(), program)
            generate_build_system.assert_called_once_with(program.root, program.files.cmake_build_dir, "develop")
            self.assertFalse(program.files.cmake_build_dir.exists())
