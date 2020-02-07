from unittest import TestCase

from mbed_tools.cli import cli
from mbed_devices.mbed_tools.cli import cli as mbed_devices_cli


class TestDevicesCommandIntegration(TestCase):
    def test_devices_is_integrated(self):
        self.assertEqual(cli.commands["devices"], mbed_devices_cli)
