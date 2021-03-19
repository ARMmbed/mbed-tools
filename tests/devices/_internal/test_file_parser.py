#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import mock

from mbed_tools.devices._internal.file_parser import (
    OnlineId,
    read_device_files,
)


class TestReadDeviceFiles:
    def test_finds_daplink_compatible_device_files(self, tmp_path):
        htm = pathlib.Path(tmp_path, "mbed.htm")
        htm.write_text("code=2222")

        info = read_device_files([tmp_path])

        assert info.product_code is not None

    def test_warns_if_no_device_files_found(self, caplog, tmp_path):
        read_device_files([tmp_path])

        assert str(tmp_path) in caplog.text

    def test_skips_hidden_files(self, caplog, tmp_path):
        auth = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={auth}&loader=11972&firmware=16457&configuration=4" />'
        )
        pathlib.Path(tmp_path, "._MBED.HTM").write_text(file_contents)

        assert read_device_files([tmp_path]).product_code is None

    def test_handles_os_error_with_warning(self, tmp_path, caplog, monkeypatch):
        bad_htm = pathlib.Path(tmp_path, "MBED.HTM")
        bad_htm.touch()
        monkeypatch.setattr(pathlib.Path, "read_text", mock.Mock(side_effect=OSError))

        read_device_files([tmp_path])
        assert str(bad_htm) in caplog.text


class TestExtractProductCodeFromHtm:
    def test_reads_product_code_from_code_attribute(self, tmp_path):
        code = "02400201B80ECE4A45F033F2"
        file_contents = f'<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code={code}"/>'
        pathlib.Path(tmp_path, "MBED.HTM").write_text(file_contents)

        assert read_device_files([tmp_path]).product_code == code[:4]

    def test_reads_product_code_from_auth_attribute(self, tmp_path):
        auth = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={auth}&loader=11972&firmware=16457&configuration=4" />'
        )
        pathlib.Path(tmp_path, "MBED.HTM").write_text(file_contents)

        assert read_device_files([tmp_path]).product_code == auth[:4]

    def test_none_if_no_product_code(self, tmp_path):
        file_contents = '<meta http-equiv="refresh" content="0; url=http://mbed.org/config" />'
        pathlib.Path(tmp_path, "MBED.HTM").write_text(file_contents)

        assert read_device_files([tmp_path]).product_code is None

    def test_extracts_first_product_code_found(self, tmp_path):
        auth = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents_1 = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={auth}&loader=11972&firmware=16457&configuration=4" />'
        )
        code = "02400201B80ECE4A45F033F2"
        file_contents_2 = f'<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code={code}"/>'
        directory_1 = pathlib.Path(tmp_path, "test-1")
        directory_1.mkdir()
        directory_2 = pathlib.Path(tmp_path, "test-2")
        directory_2.mkdir()
        pathlib.Path(directory_1, "mbed.htm").write_text(file_contents_1)
        pathlib.Path(directory_2, "mbed.htm").write_text(file_contents_2)

        result = read_device_files([directory_1, directory_2])

        assert result.product_code == auth[:4]


class TestExtractOnlineIDFromHTM:
    def test_reads_online_id_from_url(self, tmp_path):
        url = "https://os.mbed.com/platforms/THIS-IS_a_SLUG_123/"
        file_contents = f"window.location.replace({url});"
        pathlib.Path(tmp_path, "MBED.HTM").write_text(file_contents)

        assert read_device_files([tmp_path]).online_id == OnlineId(target_type="platform", slug="THIS-IS_a_SLUG_123")

    def test_none_if_not_found(self, tmp_path):
        file_contents = "window.location.replace(https://os.mbed.com/about);"
        pathlib.Path(tmp_path, "MBED.HTM").write_text(file_contents)

        assert read_device_files([tmp_path]).online_id is None
