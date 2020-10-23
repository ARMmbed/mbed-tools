#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from functools import wraps
from tempfile import TemporaryDirectory
from mbed_tools.project._internal.libraries import MbedLibReference
from mbed_tools.project._internal.project_data import (
    CMAKELISTS_FILE_NAME,
    APP_CONFIG_FILE_NAME,
    MBED_OS_REFERENCE_FILE_NAME,
)


def patchfs(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with TemporaryDirectory() as fs:
            func(*args, fs=fs, **kwargs)

    return wrapper


def make_mbed_program_files(root, config_file_name=APP_CONFIG_FILE_NAME):
    if not root.exists():
        root.mkdir()

    (root / MBED_OS_REFERENCE_FILE_NAME).touch()
    (root / config_file_name).touch()
    (root / CMAKELISTS_FILE_NAME).touch()


def make_mbed_lib_reference(root, name="mylib.lib", resolved=False, ref_url=None):
    ref_file = root / name
    source_dir = ref_file.with_suffix("")
    if not root.exists():
        root.mkdir()

    ref_file.touch()

    if resolved:
        source_dir.mkdir()

    if ref_url is not None:
        ref_file.write_text(ref_url)

    return MbedLibReference(reference_file=ref_file, source_code_path=source_dir)


def make_mbed_os_files(root):
    if not root.exists():
        root.mkdir()

    targets_dir = root / "targets"
    targets_dir.mkdir()
    (targets_dir / "targets.json").touch()
