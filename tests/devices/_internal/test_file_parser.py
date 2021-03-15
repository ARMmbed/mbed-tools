#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import mock

from mbed_tools.devices._internal.file_parser import (
    extract_product_code_from_htm,
    extract_online_id_from_htm,
    OnlineId,
    get_all_htm_files_contents,
)


class TestExtractProductCodeFromHtm:
    def test_reads_product_code_from_code_attribute(self):
        code = "02400201B80ECE4A45F033F2"
        file_contents = f'<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code={code}"/>'

        assert extract_product_code_from_htm([file_contents]) == code[:4]

    def test_reads_product_code_from_auth_attribute(self):
        auth = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={auth}&loader=11972&firmware=16457&configuration=4" />'
        )

        assert extract_product_code_from_htm([file_contents]) == auth[:4]

    def test_none_if_no_product_code(self):
        file_contents = '<meta http-equiv="refresh" content="0; url=http://mbed.org/config" />'

        assert extract_product_code_from_htm([file_contents]) is None

    def test_extracts_first_product_code_found(self):
        auth = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents_1 = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={auth}&loader=11972&firmware=16457&configuration=4" />'
        )
        code = "02400201B80ECE4A45F033F2"
        file_contents_2 = f'<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code={code}"/>'

        result = extract_product_code_from_htm([file_contents_1, file_contents_2])

        assert result == auth[:4]


class TestGetAllHTMFileContents:
    def test_skips_hidden_files(self, tmp_path):
        auth = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={auth}&loader=11972&firmware=16457&configuration=4" />'
        )
        pathlib.Path(tmp_path, "._MBED.HTM").write_text(file_contents)

        assert get_all_htm_files_contents([tmp_path]) == []

    def test_handles_os_error(self, caplog):
        mock_directory = mock.Mock()
        mock_file = mock.Mock()
        mock_file.suffix = ".HTM"
        mock_file.name = "mbed"
        mock_file.read_text.side_effect = OSError
        mock_directory.iterdir.return_value = [mock_file]

        assert get_all_htm_files_contents([mock_directory]) == []
        assert str(mock_file) in caplog.text
        mock_file.read_text.assert_called()


class TestExtractOnlineIDFromHTM:
    def test_reads_online_id_from_url(self):
        url = "https://os.mbed.com/platforms/THIS-IS_a_SLUG_123/"
        file_contents = f"window.location.replace({url});"

        assert extract_online_id_from_htm([file_contents]) == OnlineId(
            target_type="platform", slug="THIS-IS_a_SLUG_123"
        )

    def test_none_if_not_found(self):
        file_contents = "window.location.replace(https://os.mbed.com/about);"

        assert extract_online_id_from_htm([file_contents]) is None
