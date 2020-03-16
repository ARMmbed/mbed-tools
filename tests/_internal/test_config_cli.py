from click.testing import CliRunner
from unittest import TestCase, mock
from tabulate import tabulate

from mbed_tools._internal.config_cli import (
    _ConfigOption,
    _OUTPUT_PREAMBLE,
    _build_output,
    cli,
)


class TestConfigCommand(TestCase):
    @mock.patch("mbed_tools._internal.config_cli._gather_configuration_options", autospec=True)
    def test_outputs_output_built_with_gathered_configuration_options(self, _gather_configuration_options):
        result = CliRunner().invoke(cli)

        self.assertEqual(result.exit_code, 0)
        self.assertIn(_build_output(_gather_configuration_options.return_value), result.output)


class TestBuildOutput(TestCase):
    def test_merges_configuration_options_with_preamble(self):
        options = {
            _ConfigOption(key="SOME_KEY", description="Does something."),
            _ConfigOption(key="OTHER_KEY", description="Does something else."),
        }
        options_table = tabulate(
            [[option.key, option.description] for option in options], headers=["Key", "Description"]
        )
        expected_output = f"{_OUTPUT_PREAMBLE}\n{options_table}"

        self.assertEqual(expected_output, _build_output(options))
