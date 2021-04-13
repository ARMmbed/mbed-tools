#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Build configuration representation."""
import logging

from collections import UserDict
from typing import Any, Iterable, Hashable, Callable, List

from mbed_tools.build._internal.config.source import Memory, Override, ConfigSetting

logger = logging.getLogger(__name__)


class Config(UserDict):
    """Mapping of config settings.

    This object understands how to populate the different 'config sections' which all have different rules for how the
    settings are collected.
    Applies overrides, appends macros, updates memories, and updates config settings.
    """

    def __setitem__(self, key: Hashable, item: Any) -> None:
        """Set an item based on its key."""
        if key == CONFIG_SECTION:
            self._update_config_section(item)
        elif key == MEMORIES_SECTION:
            self._update_memories_section(item)
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

            try:
                setting = self._find_first_config_setting(
                    lambda x: x.name == override.name and x.namespace == override.namespace
                )
                setting.value = override.value
            except ValueError:
                logger.warning(
                    f"You are attempting to override an undefined config parameter "
                    f"`{override.namespace}.{override.name}`.\n"
                    "It is an error to override an undefined configuration parameter. "
                    "Please check your target_overrides are correct.\n"
                    f"The parameter `{override.namespace}.{override.name}` will not be added to the configuration."
                )

    def _update_config_section(self, config_settings: List[ConfigSetting]) -> None:
        for setting in config_settings:
            logger.debug("Adding config setting: '%s.%s'", setting.namespace, setting.name)
            if setting in self.data.get(CONFIG_SECTION, []):
                raise ValueError(
                    f"Setting {setting.namespace}.{setting.name} already defined. You cannot duplicate config settings!"
                )

        self.data[CONFIG_SECTION] = self.data.get(CONFIG_SECTION, []) + config_settings

    def _update_memories_section(self, memories: List[Memory]) -> None:
        defined_memories = self.data.get(MEMORIES_SECTION, [])
        for memory in memories:
            logger.debug(f"Adding memory settings `{memory.name}: start={memory.start} size={memory.size}`")
            prev_defined = next((mem for mem in defined_memories if mem.name == memory.name), None)
            if prev_defined is None:
                defined_memories.append(memory)
            else:
                logger.warning(
                    f"You are attempting to redefine `{memory.name}` from {prev_defined.namespace}.\n"
                    f"The values from `{memory.namespace}` will be ignored"
                )
        self.data[MEMORIES_SECTION] = defined_memories

    def _find_first_config_setting(self, predicate: Callable) -> Any:
        """Find first config setting based on `predicate`.

        `predicate` is a callable that gets a config setting passed in as an argument. This callable must define the
        condition for identifying a config setting.

        Example:
            The following call will find the first ConfigSetting whose name is "foo":
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
MEMORIES_SECTION = "memories"
OVERRIDES_SECTION = "overrides"


def _apply_override(data: dict, override: Override) -> None:
    if override.modifier == "add":
        data[override.name] |= override.value
    elif override.modifier == "remove":
        data[override.name] -= override.value
    else:
        data[override.name] = override.value
