#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pytest

from mbed_tools.build._internal.config import source
from mbed_tools.build._internal.config.source import Memory, Override


class TestPrepareSource:
    def test_config_fields_from_target_are_namespaced(self):
        target = {
            "config": {
                "network-default-interface-type": {
                    "help": "Default network "
                    "interface type. "
                    "Typical options: null, "
                    "ETHERNET, WIFI, "
                    "CELLULAR, MESH",
                    "value": "ETHERNET",
                }
            }
        }

        conf = source.prepare(target, "target")

        config_setting, *_ = conf["config"]
        assert config_setting.namespace == "target"
        assert config_setting.name == "network-default-interface-type"

    def test_override_fields_from_target_are_namespaced(self):
        target = {"overrides": {"network-default-interface-type": "ETHERNET"}}

        conf = source.prepare(target, "target")

        network_override, *_ = conf["overrides"]
        assert network_override.namespace == "target" and network_override.name == "network-default-interface-type"

    def test_config_fields_from_lib_are_namespaced(self):
        lib = {
            "name": "library",
            "config": {
                "network-default-interface-type": {
                    "help": "Default network "
                    "interface type. "
                    "Typical options: null, "
                    "ETHERNET, WIFI, "
                    "CELLULAR, MESH",
                    "value": "ETHERNET",
                }
            },
        }

        conf = source.prepare(lib)

        config_setting, *_ = conf["config"]
        assert config_setting.namespace == "library"
        assert config_setting.name == "network-default-interface-type"

    def test_override_fields_from_lib_are_namespaced(self):
        lib = {
            "name": "lib",
            "target_overrides": {"*": {"network-default-interface-type": "ETHERNET", "target.device_has": ["k"]}},
        }

        conf = source.prepare(lib)

        network_override, device_has_override = conf["overrides"]
        assert network_override.namespace == "lib" and network_override.name == "network-default-interface-type"
        assert device_has_override.namespace == "target" and device_has_override.name == "device_has"

    def test_target_overrides_only_collected_for_valid_targets(self):
        lib = {
            "name": "lib",
            "target_overrides": {
                "*": {"target.macros": ["j"]},
                "VALID_TARGET": {"target.device_has": ["k"]},
                "FILTER_TARGET": {"network-default-interface-type": "ETHERNET"},
            },
        }
        expected_macro_override = Override(namespace="target", name="macros", value={"j"}, modifier=None)
        expected_device_has_override = Override(namespace="target", name="device_has", value={"k"}, modifier=None)

        conf = source.prepare(lib, target_filters=["VALID_TARGET"])

        macro_override, device_has_override, *others = conf["overrides"]
        assert macro_override == expected_macro_override
        assert device_has_override == expected_device_has_override
        assert others == []

    def test_cumulative_fields_parsed(self):
        lib = {
            "name": "lib",
            "target_overrides": {
                "*": {"macros_add": ["MAC"], "target.device_has_add": ["k"], "target.device_has_remove": ["j"]}
            },
        }
        expected_device_has_add = Override(namespace="target", name="device_has", modifier="add", value={"k"})
        expected_device_has_remove = Override(namespace="target", name="device_has", modifier="remove", value={"j"})
        expected_macros_add = Override(namespace="lib", name="macros", modifier="add", value={"MAC"})

        conf = source.prepare(lib)

        macros_add_override, device_has_add_override, device_has_remove_override = conf["overrides"]
        assert device_has_add_override == expected_device_has_add
        assert device_has_remove_override == expected_device_has_remove
        assert macros_add_override == expected_macros_add

    def test_converts_config_setting_value_lists_to_sets(self):
        lib = {
            "name": "library",
            "config": {"list-values": {"value": ["ETHERNET", "WIFI"]}},
            "sectors": [[0, 2048]],
            "header_info": [[0, 2048], ["bobbins"], ["magic"]],
        }

        conf = source.prepare(lib)

        assert conf["config"][0].value == {"ETHERNET", "WIFI"}
        assert conf["sectors"] == {0, 2048}
        assert conf["header_info"] == {0, 2048, "bobbins", "magic"}

    def test_memory_attr_extracted(self):
        lib = {
            "mbed_ram_size": "0x80000",
            "mbed_ram_start": "0x24000000",
            "mbed_rom_size": "0x200000",
            "mbed_rom_start": "0x08000000",
        }

        conf = source.prepare(lib, "lib")

        assert Memory("RAM", "lib", "0x24000000", "0x80000") in conf["memories"]
        assert Memory("ROM", "lib", "0x8000000", "0x200000") in conf["memories"]

    def test_memory_attr_converted_as_hex(self):
        input_dict = {"mbed_ram_size": "1024", "mbed_ram_start": "0x24000000"}

        conf = source.prepare(input_dict, source_name="lib")

        memory, *_ = conf["memories"]
        assert memory.size == "0x400"

    def test_raises_memory_size_not_integer(self):
        input_dict = {"mbed_ram_size": "NOT INT", "mbed_ram_start": "0x24000000"}

        with pytest.raises(ValueError, match="_SIZE in lib, NOT INT is invalid: must be an integer"):
            source.prepare(input_dict, "lib")

    def test_raises_memory_start_not_integer(self):
        input_dict = {"mbed_ram_size": "0x80000", "mbed_ram_start": "NOT INT"}

        with pytest.raises(ValueError, match="_START in lib, NOT INT is invalid: must be an integer"):
            source.prepare(input_dict, "lib")

    def test_raises_memory_size_defined_not_start(self):
        input_dict = {"mbed_ram_size": "0x80000"}

        with pytest.raises(ValueError, match="Only SIZE is defined"):
            source.prepare(input_dict)

    def test_raises_memory_start_defined_not_size(self):
        input_dict = {"mbed_ram_start": "0x24000000"}

        with pytest.raises(ValueError, match="Only START is defined"):
            source.prepare(input_dict)
