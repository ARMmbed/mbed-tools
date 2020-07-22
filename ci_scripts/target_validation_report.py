#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Validate the Platform Database against the online database and render results as an HTML pages."""

import os
import sys
import logging
import argparse
import re
from collections import defaultdict
from distutils.version import StrictVersion
import requests
import jinja2
import dotenv
import datetime
from json.decoder import JSONDecodeError
from mbed_os_tools.detect.platform_database import DEFAULT_PLATFORM_DB
from mbed_tools_ci_scripts.utils.logging import set_log_level

logger = logging.getLogger(__name__)

jinja2_env = jinja2.Environment(
    loader=jinja2.PackageLoader("target_validation_report", "templates"),
    autoescape=jinja2.select_autoescape(["html", "xml"]),
)

# The name of the environment variable that needs to be set to access the target API
_AUTH_TOKEN_ENV_VAR = "MBED_API_AUTH_TOKEN"

_MBED_OS_TARGET_API = "https://os.mbed.com/api/v4/targets/all"
_MBED_OS_TARGET_JSON = "https://raw.githubusercontent.com/ARMmbed/mbed-os/master/targets/targets.json"

_OS_MBED_COM = "Online Database (os.mbed.com)"
_MBED_OS = "Mbed OS (targets.json)"
_TOOLS = "Tools Platform Database"

DATA_SOURCE_LIST = [_TOOLS, _MBED_OS, _OS_MBED_COM]

# Re to extract version numbers in the form <major.minor> and <major> e.g. "5.12" from "Mbed OS 5.12"
_version_number_re = re.compile(r"(\d+\.\d+|\d+)$")


class ProcessingError(Exception):
    """A error has occurred while processing a data source."""

    pass


def _sort_versions(version_set):
    """Sort versions using semver structure.

    Args:
        set version_set: A set of version strings in the form {"2.0", "5.12"}

    Returns:
        A sorted (highest first) non duplicate list of version numbers in the form {"5.12", "2.0"}
    """
    return sorted(version_set, key=StrictVersion, reverse=True)


def _extract_versions(mbed_os_support):
    """Extract and sort version numbers from the mbed_os_support strings.

    Args:
        mbed_os_support: A list of version strings in the form ["Mbed OS 5.12", "Mbed OS 2"]

    Returns:
        A sorted (highest first) non duplicate list of version numbers in the form ["5.12", "2.0"]
    """
    version_set = set()
    for version_string in mbed_os_support:
        match = _version_number_re.search(version_string)
        if match:
            # Get first and only match, which will be "d.d" or "d"
            version_number = match.group(1)
            # Append ".0" to any version number without a minor version i.e. "d" rather than "d.d"
            # This form of version number is required to use StrictVersion sort from distutils
            if version_number.isdigit():
                version_number += ".0"
            version_set.add(version_number)
    return _sort_versions(version_set)


class MbedOSTargetData:
    """Handle inherited values from target.json."""

    def __init__(self, target_data):
        """Retrieve the target build instructions from Mbed OS.

        Args:
            target_data: Target data retrieved from Mbed OS targets.json.
        """
        self._target_data = target_data

    def _retrieve_value(self, board_type, key):
        """Retrieve a value by traversing the hierarchy in targets.json.

        This method will recurse through the data until it finds a values.

        Args:
            board_type: The board type for which to retrieve the key.
            key: Which key to retrieve from the data.

        Returns:
            Value of key (or None if it cannot be determined) and the source board type.
        """
        value = self._target_data[board_type].get(key)
        if not value:
            try:
                # See if this board inherits from any other boards
                inherit_board_types = self._target_data[board_type]["inherits"]
            except KeyError:
                # If this board doesn't inherit from anything we have hit the end of the data
                value = None
            else:
                logger.debug(
                    "The board definition '%s' inherits from '%s'", board_type, "', '".join(inherit_board_types)
                )
                # The board can inherit from multiple definitions so try each in turn
                for inherit_board_type in inherit_board_types:
                    value, board_type = self._retrieve_value(inherit_board_type, key)
                    if value:
                        break
        return value, board_type

    def retrieve_value(self, board_type, key):
        """Retrieve a value from targets.json.

        Args:
            board_type: The board type for which to retrieve the key.
            key: Which key to retrieve from the data.

        Returns:
            Value of key or None if it cannot be determined.
        """
        value, source = self._retrieve_value(board_type, key)

        if value and source != board_type:
            logger.info("Using the '%s' value of '%s' for '%s' inherited from '%s'", key, value, board_type, source)

        return value


class PlatformValidator(object):
    """Validated known target data sources for a consistent Product ID and Board Type."""

    def __init__(self, output_dir, show_all):
        """Retrieve data from all sources.

        Args:
            output_dir: The output directory for the generated report.
            show_all: Whether to show all boards in the report or just the ones with issues.
        """
        self._output_dir = output_dir
        self._show_all = show_all

        # Global counts of the issues encountered
        self._error_count = 0
        self._warning_count = 0
        self._info_count = 0

        # The current product code being processed
        self._product_code = None
        # The current board type being processed for Mbed OS Tools
        self._tools_board_type = None

        # The results of the analysis - used when rendering the html page
        self._analysis_results = {}

        # Set of all product codes found across all sources
        self._all_product_codes = set()

        # Set of all board types found across all sources
        self._all_board_types = set()

        # Database of product codes and associated board types for each source
        # { <source name>: { <board type>: [<product codes>] } }
        self._product_code_db = {}

        # Database of board types and associated product codes for each source
        # { <source name>: { <product code>: [<board types>] } }
        self._board_type_db = {}

        # Mbed support information
        # { <source name>: {
        #     "mbed_os_support": { <product code> : [<mbed os versions>] }
        #     "mbed_enabled": { <product code> : [<mbed enabled>] } }
        # }
        self._mbed_support_db = {}

        # Metadata associate with the source
        # { <source name | *>: {
        #     "product_code_count": <int>,
        #     "board_type_count": <int> }
        # }
        self._source_meta_data = {}

        try:
            # Retrieve data from the os.mbed.com API and add to the overall set of product codes
            self._retrieve_platform_data(_OS_MBED_COM, self._os_mbed_com_source)

            # Retrieve data from the Mbed OS repository (targets.json) and add to the overall set of product codes
            self._retrieve_platform_data(_MBED_OS, self._mbed_os_source)

            # Add the local data (in this repo) into the overall set of product codes
            self._retrieve_platform_data(_TOOLS, self._tools_source)

        except ProcessingError:
            self.processing_error = True
        else:
            self.processing_error = False
            logger.info(
                "%d unique product codes for %d boards are defined in total",
                len(self._all_product_codes),
                len(self._all_board_types),
            )
            self._validate_data_source()

    def _add_products_and_boards(self, source, product_code_db, board_type_db):
        """Add to the set of all product codes and board types found across all sources.

        Args:
            source: Name of the data source.
            product_code_db: A dictionary with product codes as the keys.
            board_type_db: A dictionary with board types as the keys.
        """
        product_codes = set(product_code_db.keys())
        product_code_count = len(product_codes)
        self._all_product_codes = self._all_product_codes.union(product_codes)

        board_types = set(board_type_db.keys())
        board_type_count = len(board_types)
        self._all_board_types = self._all_board_types.union(board_types)

        self._source_meta_data[source] = {
            "product_code_count": product_code_count,
            "board_type_count": board_type_count,
        }
        self._source_meta_data["*"] = {
            "product_code_count": len(self._all_product_codes),
            "board_type_count": len(self._all_board_types),
        }
        logger.info("%s defines %d product codes for %d board types.", source, product_code_count, board_type_count)

    def _retrieve_platform_data(self, source, data_source_func):
        """Process a remote data source to obtain product codes and board types.

        Args:
            source: Name of the data source.
            data_source_func: A function which will yield a (product_code, board_type) tuple.

        Returns:
            A product code database and board type db.
        """
        # Remove duplicates as it is fine to list the product code or board type multiple times, as long as the
        # value is identical.
        product_code_db = defaultdict(set)
        board_type_db = defaultdict(set)

        mbed_os_support_db = defaultdict(list)
        mbed_enabled_db = defaultdict(list)

        for product_code, board_type, mbed_os_support, mbed_enabled in data_source_func():
            if product_code and board_type:
                board_type_db[board_type].add(product_code)
                product_code_db[product_code].add(board_type)
            if product_code and mbed_os_support:
                mbed_os_support_db[product_code].extend(_extract_versions(mbed_os_support))
            if product_code and mbed_enabled:
                mbed_enabled_db[product_code].extend(mbed_enabled)

        self._product_code_db[source] = product_code_db
        self._board_type_db[source] = board_type_db
        self._mbed_support_db[source] = {
            "mbed_os_support": mbed_os_support_db,
            "mbed_enabled": mbed_enabled_db,
        }
        self._add_products_and_boards(source, product_code_db, board_type_db)

        return product_code_db, board_type_db

    @staticmethod
    def _tools_source():
        """Yield target data from the platform database of this repo.

        Returns:
            Yield a series of (<product code>, <board type>) tuples
        """
        for product_code, board_type in DEFAULT_PLATFORM_DB["daplink"].items():
            yield product_code, board_type, None, None

    @staticmethod
    def _os_mbed_com_source():
        """Yield target data from the database hosted on os.mbed.com API.

        Also handles target data from a temporary file which includes private targets as they not currently available
        from os.mbed.com

        Returns:
            Yield a series of (<product code>, <board type>, <mbed os support>, <mbed enabled>) tuples
        """
        response = requests.get(
            _MBED_OS_TARGET_API, headers={"Authorization": "Token %s" % os.getenv(_AUTH_TOKEN_ENV_VAR)}
        )

        if response.status_code == 200:
            try:
                json_data = response.json()
            except ValueError:
                logging.error("Invalid JSON received from %s" % _MBED_OS_TARGET_API)
                raise ProcessingError()
            else:
                try:
                    target_list = json_data["data"]
                except KeyError:
                    logging.error("Invalid JSON received from %s" % _MBED_OS_TARGET_API)
                    raise ProcessingError()
                else:
                    for target in target_list:
                        attributes = target.get("attributes", {})
                        product_code = attributes.get("product_code", "").upper()
                        board_type = attributes.get("board_type", "").upper()
                        mbed_os_support = attributes.get("features", {}).get("mbed_os_support", [])
                        mbed_enabled = attributes.get("features", {}).get("mbed_enabled", [])
                        yield product_code, board_type, mbed_os_support, mbed_enabled
        elif response.status_code == 401:
            logger.error(
                "%s authentication failed (%s). Please check that the environment variable '%s' is configured "
                "with the token to access the target API. Message from the API:\n%s"
                % (_MBED_OS_TARGET_API, response.status_code, _AUTH_TOKEN_ENV_VAR, response.text)
            )
            raise ProcessingError()
        else:
            logger.error(
                "%s returned status code %s with the following message:\n%s"
                % (_MBED_OS_TARGET_API, response.status_code, response.text)
            )
            raise ProcessingError()

    def _mbed_os_source(self):
        """Yield target data from GitHub ARMmbed/mbed-os/targets/targets.json.

        Returns:
            Yield a series of (<product code>, <board type>) tuples
        """
        response = requests.get(_MBED_OS_TARGET_JSON)

        if response.status_code == 200:
            try:
                target_dict = response.json()
            except JSONDecodeError as error:
                logger.error(error)
                raise ProcessingError()
            else:
                self._target_data = {}

                target_data = MbedOSTargetData(target_dict)

                for board_type, target in target_dict.items():
                    # Board types which are not public should not be included is possible definitional
                    if target.get("public", True):
                        # Get the detect code for this board or one it inherits from
                        detect_codes = target_data.retrieve_value(board_type, "detect_code")
                        if detect_codes:
                            for detect_code in detect_codes:
                                yield detect_code, board_type, None, None

    def _add_board_types(self, os_mbed_com_board_types, mbed_os_board_types, tools_board_type):
        """Initialise the analysis results with the board types and placeholder keys for this product code.

        Args:
            os_mbed_com_board_types: List of board types from os.mbed.com.
            mbed_os_board_types: List of board types from Mbed OS.
            tools_board_type: List of board types from Tools.
        """
        initial_value = {
            "product_code": self._product_code,
            "messages": [],
            "status": {_OS_MBED_COM: "ok", _MBED_OS: "ok", _TOOLS: "ok"},
            "board_types": {
                _OS_MBED_COM: os_mbed_com_board_types,
                _MBED_OS: mbed_os_board_types,
                _TOOLS: [tools_board_type] if tools_board_type is not None else [],
            },
        }
        self._analysis_results[self._product_code] = initial_value

    def _add_message(self, sources, message, error=False, warning=False):
        """Add message, update source status for product code and update error counts.

        Args:
            sources: Single data source or list of data sources to which the message pertains.
            message: The text of the message.
            error: Set to True if this is an error message.
            warning: Set to True if this is a warning message.
        """
        results_for_product_code = self._analysis_results[self._product_code]

        # Include each source in the message text
        source_list = sources if isinstance(sources, list) else [sources]
        results_for_product_code["messages"].append("%s: %s" % (", ".join(source_list), message))

        # Set the status for each source listed
        for source in source_list:
            if error:
                results_for_product_code["status"][source] = "error"
            elif warning:
                if results_for_product_code["status"][source] != "error":
                    results_for_product_code["status"][source] = "warning"

        # Only increment the counts once for each message
        if error:
            self._error_count += 1
        elif warning:
            self._warning_count += 1
        else:
            self._info_count += 1

    @staticmethod
    def _remove_placeholders(board_types):
        """Remove place holders from a list of board types and return a new list.

        Args:
            board_types: list of board types

        Returns:
            List of board types with place holders removed.
        """
        return [board_type for board_type in board_types if "PLACEHOLDER" not in board_type]

    def _check_board_type_list(self, source, board_types):

        if None in board_types:
            self._add_message(source, "Board type value missing.", error=True)

        defined_board_types = self._remove_placeholders(board_types)
        if len(board_types) > 1:
            if len(defined_board_types) == 1:
                self._add_message(source, "Placeholder board type needs to be removed.", warning=True)
            else:
                self._add_message(source, "Different board types listed for the same product code.", error=True)

    def _check_for_mismatches(self, source, board_types):
        """Check for mismatched between the board data from different sources.

        Args:
            source: The name of the data source
            board_types: List of boards type from the defined source for the product code being processed

        Returns:
            Whether or not a match or a mismatch with the internal platform database has been found.
        """
        defined_board_types = self._remove_placeholders(board_types)
        match = False
        mismatch = False
        if defined_board_types:
            if self._tools_board_type in defined_board_types:
                match = True
            else:
                mismatch = True
        else:
            mismatched_product_codes = self._board_type_db[source][self._tools_board_type]
            if mismatched_product_codes:
                for product_code in mismatched_product_codes:
                    self._add_message(
                        source,
                        "Board type %s is associated with the product code: %s."
                        % (self._tools_board_type, product_code),
                        error=True,
                    )
            elif board_types:
                self._add_message(source, "Placeholder should be updated.", warning=True)
            else:
                if self._tools_board_type in self._board_type_db[source].keys():
                    self._add_message(source, "Product code should be added to board definition.", warning=True)
                else:
                    self._add_message(source, "Board type must be added.", error=True)

        # Check if the other board types being listed for this product code (in this data source) are associated with
        # another product code. If these product codes are not also listed for the appropriate board type in the Mbed OS
        # Tools log an error.
        for board_type in defined_board_types:
            if board_type != self._tools_board_type:
                tools_product_codes = self._board_type_db[_TOOLS][board_type]
                for product_code in self._board_type_db[source][board_type]:
                    if product_code not in tools_product_codes and product_code != self._product_code:
                        self._add_message(
                            source,
                            "Board type %s is associated with the product code: %s." % (board_type, product_code),
                            error=True,
                        )

        return match, mismatch

    def _validate_data_source(self):
        """Validate and compare data sources for consistency."""
        for self._product_code in self._all_product_codes:

            mbed_os_tools_board_types = self._product_code_db[_TOOLS].get(self._product_code)
            if mbed_os_tools_board_types is None:
                self._tools_board_type = None
            else:
                # There will be only one board type for a given product code in Mbed OS Tools due to the data structure
                self._tools_board_type = list(mbed_os_tools_board_types)[0]

            os_mbed_com_board_types = self._product_code_db[_OS_MBED_COM].get(self._product_code, [])
            mbed_os_board_types = self._product_code_db[_MBED_OS].get(self._product_code, [])

            # Initialise analysis results for this product code
            self._add_board_types(os_mbed_com_board_types, mbed_os_board_types, self._tools_board_type)

            # Product code must be alphanumeric, add an error for each source it appears in
            product_code_valid = True
            if not self._product_code.isalnum():
                for source in DATA_SOURCE_LIST:
                    if self._product_code in self._product_code_db[source]:
                        self._add_message(source, "Product code must be alphanumeric.", error=True)
                        product_code_valid = False

            if product_code_valid and self._product_code not in self._product_code_db[_OS_MBED_COM]:
                # If a product code has been found then it absolutely must be in the database, it may or may not be in
                # the other data sources
                self._add_message(_OS_MBED_COM, "Product code must be listed to reserve the number.", error=True)

            self._check_board_type_list(_OS_MBED_COM, os_mbed_com_board_types)
            self._check_board_type_list(_MBED_OS, mbed_os_board_types)

            if self._tools_board_type:
                if "PLACEHOLDER" in self._tools_board_type:
                    self._add_message(_TOOLS, "Placeholder board type should be removed.", warning=True)
                else:
                    os_mbed_com_match, os_mbed_com_mismatch = self._check_for_mismatches(
                        _OS_MBED_COM, os_mbed_com_board_types
                    )
                    mbed_os_match, mbed_os_mismatch = self._check_for_mismatches(_MBED_OS, mbed_os_board_types)

                    if os_mbed_com_mismatch and mbed_os_mismatch:
                        self._add_message(_TOOLS, "Board type incorrectly defined.", error=True)
                    elif os_mbed_com_mismatch:
                        if mbed_os_match:
                            self._add_message(_OS_MBED_COM, "Board type incorrectly defined.", error=True)
                        else:
                            self._add_message([_OS_MBED_COM, _TOOLS], "Board types do not match.", error=True)
                    elif mbed_os_mismatch:
                        if os_mbed_com_match:
                            self._add_message(_MBED_OS, "Board type incorrectly defined.", error=True)
                        else:
                            self._add_message([_MBED_OS, _TOOLS], "Board types do not match.", error=True)

        logger.info("Errors: %d, Warnings %d, Infos: %d.", self._error_count, self._warning_count, self._info_count)

    def _render_templates(self, template_files, **template_kwargs):
        """Render one or more jinja2 templates.

        The output name is based on the template name (with the final extension removed).

        Args:
            template_files: List of of template file names.
            template_kwargs: Keyword arguments to pass to the render method.
        """
        for template_name in template_files:
            output_name = template_name.rsplit(".", 1)[0]
            output_path = os.path.join(self._output_dir, output_name)
            logger.info("Rendering template from %s to %s" % (template_name, output_path))
            template = jinja2_env.get_template(template_name)
            rendered = template.render(**template_kwargs)
            with open(output_path, "w", encoding="utf-8") as output_file:
                output_file.write(rendered)

    def render_results(self):
        """Render summary results page in html."""
        if self.processing_error:
            logger.warning("Unable to render results due to error processing source data.")
        else:
            # Setup the key word arguments to pass to the jinja2 template
            template_kwargs = {
                "data_sources": DATA_SOURCE_LIST,
                "analysis_results": self._analysis_results,
                "mbed_support": self._mbed_support_db[_OS_MBED_COM],
                "meta_data": self._source_meta_data,
                "show_all": self._show_all,
                "error_count": self._error_count,
                "warning_count": self._warning_count,
                "info_count": self._info_count,
                "render_time": datetime.datetime.now(),
            }

            # Re-render the index templates to reflect the new verification data.
            self._render_templates(("index.html.jinja2",), **template_kwargs)


def main():
    """Handle command line arguments to generate a results summary file."""
    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--output-dir", type=str, help="Output directory for the summary report.")
    parser.add_argument("-a", "--show-all", action="store_true", help="Show all boards in report not just issues.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbosity, by default errors are reported.")

    arguments = parser.parse_args()
    set_log_level(arguments.verbose)

    # Path to the output directory
    if arguments.output_dir is None:
        output_dir = os.getcwd()
    else:
        output_dir = arguments.output_dir

    # Retrieve environment settings (if any) stored in a .env file
    dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True, raise_error_if_not_found=False))

    platform_validator = PlatformValidator(output_dir, arguments.show_all)
    platform_validator.render_results()

    return platform_validator.processing_error


if __name__ == "__main__":
    sys.exit(main())
