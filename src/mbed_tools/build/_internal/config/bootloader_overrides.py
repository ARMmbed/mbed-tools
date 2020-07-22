#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Ability to parse bootloader overrides from Sources."""
from dataclasses import dataclass, field, fields
from typing import Any, Iterable, Optional

from mbed_tools.build._internal.config.source import Source


@dataclass
class BootloaderOverride:
    """Representation of a bootloader override."""

    value: Any
    name: str
    set_by: str


@dataclass
class BootloaderOverrides:
    """Representation of cumulative attributes assembled during Source parsing."""

    # delivery overrides
    deliver_to_target: Optional[BootloaderOverride] = field(default=None)
    deliver_artifacts: Optional[BootloaderOverride] = field(default=None)
    delivery_dir: Optional[BootloaderOverride] = field(default=None)

    # rom overrides managed BL
    bootloader_img: Optional[BootloaderOverride] = field(default=None)
    restrict_size: Optional[BootloaderOverride] = field(default=None)
    header_format: Optional[BootloaderOverride] = field(default=None)
    header_offset: Optional[BootloaderOverride] = field(default=None)
    app_offset: Optional[BootloaderOverride] = field(default=None)
    # rom overrides unmanaged BL
    mbed_app_start: Optional[BootloaderOverride] = field(default=None)
    mbed_app_size: Optional[BootloaderOverride] = field(default=None)
    # rom overrides managed/unmanaged BL
    mbed_rom_start: Optional[BootloaderOverride] = field(default=None)
    mbed_rom_size: Optional[BootloaderOverride] = field(default=None)

    # ram overrides
    mbed_ram_start: Optional[BootloaderOverride] = field(default=None)
    mbed_ram_size: Optional[BootloaderOverride] = field(default=None)

    @classmethod
    def from_sources(cls, sources: Iterable[Source]) -> "BootloaderOverrides":
        """Interrogate each Source in turn to create BootloaderOverrides."""
        data = BootloaderOverrides()
        for source in sources:
            for key, value in source.overrides.items():
                if key in BOOTLOADER_OVERRIDE_KEYS_IN_SOURCE:
                    key_without_prefix = key[len("target.") :]
                    setattr(
                        data,
                        key_without_prefix,
                        BootloaderOverride(name=key_without_prefix, value=value, set_by=source.human_name),
                    )
        return data


_BOOTLOADER_OVERRIDE_FIELDS = [f.name for f in fields(BootloaderOverrides)]
BOOTLOADER_OVERRIDE_KEYS_IN_SOURCE = [f"target.{f}" for f in _BOOTLOADER_OVERRIDE_FIELDS]
