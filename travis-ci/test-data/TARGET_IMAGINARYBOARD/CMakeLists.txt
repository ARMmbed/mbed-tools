# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

add_library(mbed-imaginaryboard INTERFACE)

target_sources(mbed-imaginaryboard
    INTERFACE
        PeripheralPins.c
)

target_include_directories(mbed-imaginaryboard
    INTERFACE
        .
)

target_link_libraries(mbed-imaginaryboard INTERFACE mbed-stm32l475xg)
