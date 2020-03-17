from click.testing import CliRunner
from unittest import TestCase, mock
from mbed_devices.mbed_tools import config_variables as mbed_devices_config_variables

from mbed_tools._internal.config_cli import (
    _OUTPUT_PREAMBLE,
    _build_output,
    _gather_configuration_variables,
    _tab_prefix,
    cli,
)


class TestConfigCommand(TestCase):
    @mock.patch("mbed_tools._internal.config_cli._gather_configuration_variables", autospec=True)
    def test_outputs_output_built_with_gathered_configuration_variables(self, _gather_configuration_variables):
        result = CliRunner().invoke(cli)

        self.assertEqual(result.exit_code, 0)
        self.assertIn(_build_output(_gather_configuration_variables.return_value), result.output)


class TestGatherConfigurationVariables(TestCase):
    def test_returns_all_dependencies_configuration_variables(self):
        self.assertEqual(_gather_configuration_variables(), mbed_devices_config_variables)


class TestBuildOutput(TestCase):
    def test_prints_preamble(self):
        config_var = mock.Mock(docstring="Foo doc")
        config_var.name = "FOO"
        variable_output = f"{config_var.name}\n\n{_tab_prefix(config_var.docstring)}"

        expected_output = f"{_OUTPUT_PREAMBLE}\n\n{variable_output}"

        self.assertEqual(expected_output, _build_output([config_var]))


class TestTabPrefix(TestCase):
    def test_prefixes_all_lines_with_tab(self):
        self.assertEqual("\tHAT\n\tBOAT", _tab_prefix("HAT\nBOAT"))
