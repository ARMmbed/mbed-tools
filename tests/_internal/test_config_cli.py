from click.testing import CliRunner
from unittest import TestCase, mock

from mbed_tools._internal.config_cli import (
    _OUTPUT_PREAMBLE,
    _build_output,
    _tab_prefix,
    cli,
)


class TestConfigCommand(TestCase):
    @mock.patch("mbed_tools._internal.config_cli._gather_configuration_variables", autospec=True)
    def test_outputs_output_built_with_gathered_configuration_variables(self, _gather_configuration_variables):
        result = CliRunner().invoke(cli)

        self.assertEqual(result.exit_code, 0)
        self.assertIn(_build_output(_gather_configuration_variables.return_value), result.output)


class TestBuildOutput(TestCase):
    def test_prints_preamble(self):
        config_var = mock.Mock(docstring="Foo doc")
        config_var.name = "FOO"
        self.maxDiff = None

        expected_output = f"{_OUTPUT_PREAMBLE}\n\n{config_var.name}\n\n\t{config_var.docstring}"

        self.assertEqual(expected_output, _build_output([config_var]))


class TestTabPrefix(TestCase):
    def test_prefixes_all_lines_with_tab(self):
        self.assertEqual("\tHAT\n\tBOAT", _tab_prefix("HAT\nBOAT"))
