#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Build configuration representation."""
import logging

from collections import UserDict
from typing import Any, Iterable, Hashable, Callable, List

from mbed_tools.build._internal.config.source import Override, ConfigSetting

logger = logging.getLogger(__name__)


class Config(UserDict):
    """Mapping of config settings.

    This object understands how to populate the different 'config sections' which all have different rules for how the
    settings are collected.
    Applies overrides, appends macros and updates config settings.
    """

    def __setitem__(self, key: Hashable, item: Any) -> None:
        """Set an item based on its key."""
        if key == CONFIG_SECTION:
            self._update_config_section(item)
        elif key == OVERRIDES_SECTION:
            self._handle_overrides(item)
        elif key == MACROS_SECTION:
            self.data[MACROS_SECTION] = self.data.get(MACROS_SECTION, set()) | item
        else:
            super().__setitem__(key, item)

    def _handle_overrides(self, overrides: Iterable[Override]) -> None:
        for override in overrides:
            logger.debug("Applying override '%s.%s'='%s'", override.namespace, override.name, repr(override.value))
            if override.name == "requires":
                self.data["requires"] = self.data.get("requires", set()) | override.value
                continue

            if override.name in self.data:
                _apply_override(self.data, override)
                continue

            setting = self._find_config_setting(lambda x: x.name == override.name and x.namespace == override.namespace)
            setting.value = override.value

    def _update_config_section(self, config_settings: List[ConfigSetting]) -> None:
        for setting in config_settings:
            logger.debug("Adding config setting: '%s.%s'", setting.namespace, setting.name)
            if setting in self.data.get(CONFIG_SECTION, []):
                raise ValueError(
                    f"Setting {setting.namespace}.{setting.name} already defined. You cannot duplicate config settings!"
                )

        self.data[CONFIG_SECTION] = self.data.get(CONFIG_SECTION, []) + config_settings

    def _find_config_setting(self, predicate: Callable) -> Any:
        """Find a config setting based on `predicate`.

        `predicate` is a callable that gets a config setting passed in as an argument. This callable must define the
        condition for identifying a config setting.

        Example:
            The following call will find a ConfigSetting whose name is "foo":
            `config._find_config_setting(lambda x: x.name == "foo")`

        Args:
            predicate: A callable that returns True when the desired setting is found.
        """
        for elem in self.data.get(CONFIG_SECTION, []):
            if predicate(elem):
                return elem

        raise ValueError("Could not find element.")


CONFIG_SECTION = "config"
MACROS_SECTION = "macros"
OVERRIDES_SECTION = "overrides"


def _apply_override(data: dict, override: Override) -> None:
    if override.modifier == "add":
        data[override.name] |= override.value
    elif override.modifier == "remove":
        data[override.name] -= override.value
    else:
        data[override.name] = override.value
