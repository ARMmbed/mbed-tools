#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

from mbed_tools.devices._internal.htm_file import read_product_code, read_online_id, OnlineId


class TestReadProductCode(TestCase):
    def test_reads_product_code_from_code_attribute(self):
        code = "02400201B80ECE4A45F033F2"
        file_contents = f'<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code={code}"/>'

        self.assertEqual(read_product_code(file_contents), code[:4])

    def test_reads_product_code_from_auth_attribute(self):
        auth = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={auth}&loader=11972&firmware=16457&configuration=4" />'
        )

        self.assertEqual(read_product_code(file_contents), auth[:4])

    def test_none_if_no_product_code(self):
        self.assertIsNone(read_product_code(""))


class TestReadOnlineId(TestCase):
    def test_reads_online_id_from_url(self):
        url = "https://os.mbed.com/platforms/THIS-IS_a_SLUG_123/"
        file_contents = f"window.location.replace({url});"

        self.assertEqual(read_online_id(file_contents), OnlineId(target_type="platform", slug="THIS-IS_a_SLUG_123"))

    def test_none_if_not_found(self):
        file_contents = "window.location.replace(https://os.mbed.com/about);"
        self.assertIsNone(read_online_id(file_contents))
