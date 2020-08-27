# Mbed Tools

Starting with version 6.x, Mbed OS is moving from Mbed CLI to a new build tool: it's cmake-based,
You'll still need Mbed CLI for older versions of Mbed OS. You can install both tools side by side.


# Install or upgrade

Mbed Tools is Python based, so you can install it with pip.

**Tip:** We recommend using a virtual environment such as [Pipenv](https://github.com/pypa/pipenv/blob/master/README.md) to avoid Python dependency conflicts.

## Prerequisite

- Python 3.6 or newer. Install for [Windows](https://docs.python.org/3/using/windows.html), [Linux](https://docs.python.org/3/using/unix.html) or [macOS](https://docs.python.org/3/using/mac.html).
- Pip (if not included in your Python installation). [Install for all operating systems](https://pip.pypa.io/en/stable/installing/).
- cmake. [Install version 3.18.1 or newer for all operating systems](https://cmake.org/install/).
- Ninja [Install version 1.0 or newer for all operating systems](https://github.com/ninja-build/ninja/wiki/Pre-built-Ninja-packages).

## Install

Use pip to install:

- To install the latest release:

    ```
    python -m pip install mbed-tools
    ```

- To install a specific version:

    ```
    python -m pip install mbed-tools==<version number in major.minor.patch format>
    ```

- To install a pre-release or development version:

    ```
    python -m pip install mbed-tools --pre
    ```

## Upgrade

Use pip to upgrade:

```
python -m pip install mbed-tools --upgrade
```

# Use

For help:

- To get help for all commands, use:

    ```
    mbed-tools --help
    ```

- To get help for a specific command, use `mbed-tools <command> --help`. For example, for helping with listing connected devices (the `devices` command):

    ```
    mbed-tools devices --help
    ```

## Create a project

You can create a new project or create a local copy of one of our example applications.

### Create a new project

To create a new Mbed OS project in a specified path:

- To create the project and download a new copy of Mbed OS (latest official release):

    ```
    mbed-tools init <PATH>
    ```

    The path can be:
    - Absolute. `init` will create the folder if it doesn't exist.
    - Relative.

    If you have already created a project folder, you can use `.`

    If you want the `init` command to create a project folder, use `.\<folder-name>`.

- To create a project without downloading a copy of Mbed OS (reuse an existing copy):

    ```
    mbed-tools init -c <PATH>
    ```

### Use an example application

To create a local copy of an example application, use the `clone` command with the example name or full GitHub URL listed below:

```
mbed-tools clone <example> <PATH>
````

- [mbed-os-example-blinky](https://github.com/ARMmbed/mbed-os-example-blinky)
- [mbed-os-example-ble](https://github.com/ARMmbed/mbed-os-example-ble) - use the BLE button example.
- [mbed-os-example-cellular](https://github.com/ARMmbed/mbed-os-example-cellular)
- [mbed-os-example-devicekey](https://github.com/ARMmbed/mbed-os-example-devicekey)
- [mbed-os-example-kvstore](https://github.com/ARMmbed/mbed-os-example-kvstore)
- [mbed-os-example-lorawan](https://github.com/ARMmbed/mbed-os-example-lorawan)
- [mbed-os-example-mbed-crypto](https://github.com/ARMmbed/mbed-os-example-mbed-crypto)
- [mbed-os-example-nfc](https://github.com/ARMmbed/mbed-os-example-nfc)
- [mbed-os-example-sockets](https://github.com/ARMmbed/mbed-os-example-sockets)

## Configure the project

Each project depends on two sets of configurations:

- The project's environment variables. You can use the default values.
- The Mbed OS configuration system. You must set up your target and toolchain.

### Project environment variables (Optional)

Mbed Tools has two environment variables that you can set for a project:

- `MBED_API_AUTH_TOKEN`: Token to access private board information stored for a vendor team.
- `MBED_DATABASE_MODE`: Use online or offline mode. Possible values:
    - `AUTO`: Search the offline database first; search the online database only if the board wasn't found offline. This is the default value.
    - `ONLINE`: Alway use the online database.
    - `OFFLINE`: Always use the offline database.

To set values, create an `.env` file in the root directory of the project. The file should contain definitions in the `<VARIABLE>=<value>` format.

For more information on overriding defaults, use

```
mbed-tools env
```

### Mbed OS configuration

The Mbed OS configuration system parses the configuration files in your project (mbed_lib.json, mbed_app.json and targets.json) for a particular target and toolchain, and outputs a CMake script. The build system uses this script to build for your target, using your toolchain.

**Tip:** If you're rebuilding for the same target and toolchain, you can keep using the same CMake script, so you won't have to use the `configure` command again for each build. If you change any of mbed_lib.json, mbed_app.json, targets.json, target or toolchain, run the `configure` command again to generate a new CMake script.

1. Check your board's build target name.

    Connect your board over USB and run the `devices` command:

    ```
    mbed-tools devices
    Board name    Serial number             Serial port             Mount point(s)    Build target(s)
    ------------  ------------------------  ----------------------  ----------------  -----------------
    FRDM-K64F     024002017BD34E0F862DB3B7  /dev/tty.usbmodem14402  /Volumes/MBED     K64F
    ```
1. To prepare the Mbed configuration information for use with a specific target and toolchain, navigate to the project's root folder and run:

    ```
    mbed-tools configure -m <target> -t <toolchain>
    ```

    - The supported targets are `K64F`, `DISCO_L475VG_IOT01A`, `NRF52840_DK`
    - The supported toolchains are `GCC_ARM` and `ARM`.

    Example for FRDM-K64F and GCC:

    ```
    mbed-tools configure -m K64F -t GCC_ARM
    mbed_config.cmake has been generated and written to '/Users/UserName/Development/Blinky/.mbedbuild'
    ```

## Build the project

Currently, the new Cmake system supports three boards: `K64F`, `DISCO_L475VG_IOT01A` and `NRF52840_DK`.

Use CMake to build your application:

1. Navigate to the project's root folder.
1. Set the build parameters:

    ```
    cmake -S . -B cmake_build -GNinja -DCMAKE_BUILD_TYPE=<profile>
    ```
    - -S <path-to-source>: Path to the root directory of the CMake project. We use `.` to indicate we're building from the current directory.<!--at no point until now did we tell them to navigate to the directory, though-->
    - -B <path-to-build>: Path to the build output directory. If the directory doesn't already exist, CMake will create it. We use `cmake_build` as the output directory name; you can use a different name.
    - -GNinja: To use the Ninja tool.
    - -DCMAKE_BUILD_TYPE: Build type. The value (`profile`) can be `release`, `debug` or `develop`.

1. Build:

    ```
    cmake --build cmake_build
    ```

    This generates two files in the build output directory (`cmake_build` in this example): HEX and BIN.

1. Drag and drop the generated file to your board.

## Logging

To specify the log level, use the verbose logging option (`-v`) before the first argument.

If you don't use `-v`, by default the log will show only errors. These are the following log levels:

- `-v`: Warning and errors.
- `-vv`: Information, warning and errors.
- `-vvv`: Debug, information, warning and errors.

For example:

```
mbed-tools -vv configure -m <target> -t <toolchain>
```
