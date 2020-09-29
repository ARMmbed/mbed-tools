#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Build configuration representation."""
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional

from mbed_tools.build._internal.config.source import Source
from mbed_tools.build._internal.config.cumulative_data import CUMULATIVE_OVERRIDE_KEYS_IN_SOURCE
from mbed_tools.build._internal.config.bootloader_overrides import BOOTLOADER_OVERRIDE_KEYS_IN_SOURCE


@dataclass
class Macro:
    """Representation of a macro."""

    value: Any
    name: str
    set_by: str

    @classmethod
    def build(cls, macro: str, source: Source) -> "Macro":
        """Build macro from macro string.

        There are two flavours of macro strings in MbedOS configuration:
        - with value: FOO=BAR
        - without value: FOO
        """
        value: Any
        if "=" in macro:
            name, value = macro.split("=")
        else:
            name = macro
            value = None

        return cls(name=name, value=value, set_by=source.human_name)


@dataclass
class Option:
    """Representation of a configuration option."""

    value: Any
    macro_name: Optional[str]
    help_text: Optional[str]
    set_by: str
    key: str

    @classmethod
    def build(cls, key: str, data: Any, source: Source) -> "Option":
        """Build configuration option from config entry value.

        Config values are either complex data structures or simple values.
        This function handles both.

        Args:
            key: Namespaced configuration key
            data: Configuration data - a dict or a primitive
            source: Source from which option data came - used for tracing overrides
        """
        if isinstance(data, dict):
            return cls(
                key=key,
                value=_sanitize_option_value(data.get("value")),
                macro_name=data.get("macro_name", _build_option_macro_name(key)),
                help_text=data.get("help"),
                set_by=source.human_name,
            )
        else:
            return cls(
                value=_sanitize_option_value(data),
                key=key,
                macro_name=_build_option_macro_name(key),
                help_text=None,
                set_by=source.human_name,
            )

    def set_value(self, value: Any, source: Source) -> "Option":
        """Mutate self with new value."""
        self.value = _sanitize_option_value(value)
        self.set_by = source.human_name
        return self


IGNORED_OVERRIDE_KEYS_IN_SOURCE = CUMULATIVE_OVERRIDE_KEYS_IN_SOURCE + BOOTLOADER_OVERRIDE_KEYS_IN_SOURCE


@dataclass
class Config:
    """Representation of config attributes assembled during Source parsing.

    Attributes:
        options: Options parsed from "config" and "target_overrides" sections of *.json files
        macros: Macros parsed from "macros" section of mbed_lib.json and mbed_app.json file
    """

    options: Dict[str, Option] = field(default_factory=dict)
    macros: Dict[str, Macro] = field(default_factory=dict)

    @classmethod
    def from_sources(cls, sources: Iterable[Source]) -> "Config":
        """Interrogate each source in turn to create final Config."""
        config = Config()
        for source in sources:
            for key, value in source.config.items():
                # If the config item is about a certain component or feature
                # being present, avoid adding it to the mbed_config.cmake
                # configuration file. Instead, applications should depend on
                # the feature or component with target_link_libraries() and the
                # component's CMake flle (in the Mbed OS repo) will create
                # any necessary macros or definitions.
                if key.endswith(".present"):
                    continue
                _create_config_option(config, key, value, source)
            for key, value in source.overrides.items():
                if key in IGNORED_OVERRIDE_KEYS_IN_SOURCE:
                    continue
                _update_config_option(config, key, value, source)
            for value in source.macros:
                _create_macro(config, value, source)
        return config


def _create_config_option(config: Config, key: str, value: Any, source: Source) -> None:
    """Mutates Config in place by creating a new Option."""
    config.options[key] = Option.build(key, value, source)


def _update_config_option(config: Config, key: str, value: Any, source: Source) -> None:
    """Mutates Config in place by updating the value of existing Option."""
    if key not in config.options:
        raise ValueError(
            f"Can't update option which does not exist."
            f" Attempting to set '{key}' to '{value}' in '{source.human_name}'."
        )
    config.options[key].set_value(value, source)


def _build_option_macro_name(config_key: str) -> str:
    """Build macro name for configuration key.

    All configuration variables require a macro name, so that they can be referenced in a header file.
    Some values in config define "macro_name", some don't. This helps generate consistent macro names
    for the latter.
    """
    sanitised_config_key = config_key.replace(".", "_").replace("-", "_").upper()
    return f"MBED_CONF_{sanitised_config_key}"


def _sanitize_option_value(value: Any) -> Any:
    """Converts booleans to ints, leaves everything else as is."""
    if isinstance(value, bool):
        return int(value)
    else:
        return value


def _create_macro(config: Config, macro_str: str, source: Source) -> None:
    """Mutates Config in place by creating a new macro."""
    macro = Macro.build(macro_str, source)
    existing = config.macros.get(macro.name)
    if existing:
        raise ValueError(
            f"Can't override previously set macro."
            f" Attempting to set '{macro.name}' to '{macro.value}' in '{source.human_name}'."
            f" Set previously by '{existing.set_by}'."
        )
    config.macros[macro.name] = macro
