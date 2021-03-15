#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib
import tempfile

from mbed_tools.devices._internal.file_parser import (
    read_product_code,
    read_online_id,
    OnlineId,
    _is_htm_file,
    get_all_htm_files_contents,
    _read_htm_file_contents,
)


class TestReadProductCode:
    def test_reads_product_code_from_code_attribute(self):
        code = "02400201B80ECE4A45F033F2"
        file_contents = f'<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code={code}"/>'

        assert read_product_code(file_contents) == code[:4]

    def test_reads_product_code_from_auth_attribute(self):
        auth = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={auth}&loader=11972&firmware=16457&configuration=4" />'
        )

        assert read_product_code(file_contents) == auth[:4]

    def test_none_if_no_product_code(self):
        assert read_product_code("") is None


class TestReadOnlineId:
    def test_reads_online_id_from_url(self):
        url = "https://os.mbed.com/platforms/THIS-IS_a_SLUG_123/"
        file_contents = f"window.location.replace({url});"

        assert read_online_id(file_contents) == OnlineId(target_type="platform", slug="THIS-IS_a_SLUG_123")

    def test_none_if_not_found(self):
        file_contents = "window.location.replace(https://os.mbed.com/about);"
        assert read_online_id(file_contents) is None


class TestGetAllHtmFilesContents:
    def test_returns_contents_of_all_htm_files_in_given_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_1 = pathlib.Path(directory, "test-1")
            directory_1.mkdir()
            directory_2 = pathlib.Path(directory, "test-2")
            directory_2.mkdir()
            pathlib.Path(directory_1, "mbed.htm").write_text("foo")
            pathlib.Path(directory_2, "whatever.htm").write_text("bar")
            pathlib.Path(directory_1, "file.txt").write_text("txt files should not be read")
            pathlib.Path(directory_1, "._MBED.HTM").write_text("hidden files should not be read")

            result = get_all_htm_files_contents([directory_1, directory_2])

        assert result == ["foo", "bar"]


class TestReadHtmFilesContents:
    def test_handles_unreadable_htm_file(self):
        with tempfile.TemporaryDirectory() as directory:
            htm_file = pathlib.Path(directory, "mbed.htm")
            htm_file.write_text("foo")

            result = _read_htm_file_contents([htm_file, pathlib.Path("error.htm")])

        assert result == ["foo"]


class TestIsHtmFile:
    def test_lower_case_htm(self):
        result = _is_htm_file(pathlib.Path("mbed.htm"))
        assert result is True

    def test_upper_case_htm(self):
        result = _is_htm_file(pathlib.Path("MBED.HTM"))
        assert result is True

    def test_hidden_htm(self):
        result = _is_htm_file(pathlib.Path(".htm"))
        assert result is False

    def test_text_file(self):
        result = _is_htm_file(pathlib.Path("mbed.txt"))
        assert result is False
