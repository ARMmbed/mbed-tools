# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

add_library(IMAGINARYBOARD INTERFACE)

target_sources(IMAGINARYBOARD
    INTERFACE
        PeripheralPins.c
)

target_include_directories(IMAGINARYBOARD
    INTERFACE
        .
)

target_link_libraries(IMAGINARYBOARD INTERFACE STM32L475xG)
