# 2. Move mbed config header defines to CMake

Date: 2020-07-23

## Status

Accepted

## Context

`mbed_config.h` was created because the command line length limit on older versions of Windows prevented passing many "-D" defines to the compiler and linker.
Additionally, passing many "-D" defines globally is a bad idea in itself. Therefore, `mbed_config.h` was a workaround to make a bad practice work.
On modern versions of Windows, the command line limit isn't an issue. CMake can also do what's necessary to prevent exceeding the command line length limit where needed.

## Decision

We will remove the generation of `mbed_config.h` and simply pass the "-D" defines using CMake directives. This is acheived by moving the "-D" definitions to the tools generated `mbed_config.cmake`.

## Consequences

CMake will be in control of passing the defines to the compiler. The tools generate a single file containing all dynamic configuration parameters.
This model will make it easier to modularise the build system later, as we are removing a "global" header that is included everywhere.
