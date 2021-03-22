# Migration guide

If you haven't already read the [introduction](./intro.md), then start from there.

The background color indicates:

* <span style="background-color:green;color:black">Green: New Functionality
  introduced in Mbed CLI 2 (mbed-tools)</span>
* <span style="background-color:orange;color:black">Orange: Functionality
  modified in Mbed CLI 2 (mbed-tools) compared to Mbed CLI 1 (mbed-cli)</span>
* <span style="background-color:red;color:black">Red: Functionality deprecated
  in Mbed CLI 2 (mbed-tools)</span>

## Installers
<span style="background-color:orange;color:black">Windows, macOS and Linux
installers may be made available at later point of time.</span><br>

## Commands

### Device management
<span style="background-color:red;color:black">The subcommand "mbed-cli
device-management (device management) is deprecated. Refer to your cloud
provider's documentation on how to cloud-manage your devices.</span><br>

### Repository management
<span style="background-color:red;color:black">Support for "Mercurial" and the
subcommand "mbed-cli publish (Publish program or library)" is deprecated.
Hosted repositories on "mbed.org" are no longer supported. Version control with
"git" can be used as an alternative.</span><br>

<span style="background-color:red;color:black">The subcommand "mbed-cli cache
(Repository cache management)" is deprecated. No replacement is
supported.</span><br>

<span style="background-color:red;color:black">The subcommand "mbed-cli
releases (Show release tags)" is deprecated. We recommend using standard "git"
commands instead, for example `git tag -l` to list all tagged
releases.</span><br>

<span style="background-color:orange;color:black">The subcommand "mbed-cli
update (Update to branch, tag, revision or latest)" is not implemented. Use
standard "git" commands instead. From your application directory: to check out
a branch of Mbed OS, `git -C mbed-os checkout branchname`; to checkout the Mbed
OS 6.8.0 release, `git -C mbed-os checkout mbed-os-6.8.0`; to check out Mbed OS
revision `3e24a7ea9602`, `git -C mbed-os checkout 3e24a7ea9602`; to checkout
the latest released version of Mbed OS `git -C mbed-os checkout
latest`.</span><br>

<span style="background-color:red;color:black">The subcommand "mbed-cli export
(Generate an IDE project)" is deprecated. Use ["CMake"
generators](https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html)
instead.
While CMake supports many generators, including many not supported by Mbed CLI
1, not all of Mbed CLI 1's exporters have replacements available yet. The
available project generators are listed below.</span><br>

- [CodeBlocks](https://cmake.org/cmake/help/latest/generator/CodeBlocks.html)
- [Eclipse](https://cmake.org/cmake/help/latest/generator/Eclipse%20CDT4.html)
- [Make](https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html#id10)
- [Qt Creator](https://doc.qt.io/qtcreator/creator-project-cmake.html)
- [Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools)

<span style="background-color:red;color:black">If you'd like to help us
prioritize which CMake project generators to work on first, please give your
thumbs up to the following issues you care most about:</span><br>

- [CrossCore® Embedded Studio](https://github.com/ARMmbed/mbed-tools/issues/249)
- [e<sup>2</sup> studio](https://github.com/ARMmbed/mbed-tools/issues/250)
- [Embitz](https://github.com/ARMmbed/mbed-tools/issues/251)
- [IAR Embedded Workbench for Arm](https://github.com/ARMmbed/mbed-tools/issues/252)
- [MCUXpresso](https://github.com/ARMmbed/mbed-tools/issues/253)
- [NetBeans](https://github.com/ARMmbed/mbed-tools/issues/254)
- [STM32CubeIDE](https://github.com/ARMmbed/mbed-tools/issues/257)
- [Keil uVision](https://github.com/ARMmbed/mbed-tools/issues/256)

### Library management
<span style="background-color:red;color:black">The subcommand "mbed-cli add
(Add library from URL)" and "mbed-cli remove (Remove library) is deprecated.
Instead, use "git clone" or "mbed-tools import" to clone a library. Then,
manually create a `reponame.lib` file that contains a single line like
`https://github.com/ARMmbed/reponame#branch-or-tag`, pointing to your repo at
the default branch (no `#` and nothing after the `#`), desired tag (append with
`#tagname`), or desired branch (append with `#branchname`).</span><br>

<span style="background-color:red;color:black">The subcommand "mbed-cli new
--library (Force creation of an Mbed library)" is deprecated. Create a new Mbed
library by hand instead, using standard "git" commands.</span><br>

<span style="background-color:red;color:black">The subcommand "mbed-cli ls
(View dependency tree)" is deprecated. Use `mbed-tools deploy`
instead to list dependencies.</span><br>

### Tool configuration
<span style="background-color:red;color:black">"mbed-cli config (Tool
configuration)" is deprecated. There is no need to configure compiler path in
Mbed CLI 2 as it is handled by "CMake". However, other configuration options
"target", "toolchain", "protocol", "depth" and "cache" are not supported in
Mbed CLI 2.</span><br>

<span style="background-color:red;color:black">The subcommand "mbed-cli
toolchain (Set or get default toolchain)" is deprecated.</span><br>

<span style="background-color:red;color:black">The subcommand "mbed-cli target
(Set or get default target)" is deprecated.</span><br>


### Creating an Mbed program
<span style="background-color:orange;color:black">The subcommand "mbed-tools
new" creates a new Mbed program by default and supports only one
command-line-option "--create-only (Create a program without fetching
mbed-os)". The other command-line-options supported in Mbed CLI 1 "--scm",
"--program", "--library", "--mbedlib", "--depth", "--protocol", "--offline",
and "--no-requirements" are deprecated.</span><br>

### Importing an Mbed program
<span style="background-color:orange;color:black">The subcommand "mbed-tools
import" clones an Mbed project and library dependencies. But the following
command-line-options supported in Mbed CLI 1 are deprecated:

* --depth: The new CLI optimistically imports the most shallow repository
  possible. Running `git clone --depth <depth> <repo_url> | cd <repo_name> &&
  mbed-tools deploy` will create an mbed project with the required depth.
* --protocol: To select the protocol, simply import using the URL for the
  desired protocol. For instance, the tool allows you to import projects or
  libraries over SSH as follows `mbed-tools import
  git://github.com/ARMmbed/<some_driver>`. Alternatively, if you would prefer
  to use SSH you can add the following into your .gitconfig to force the tool
  to use it instead.

```sh
[url "ssh://git@github.com/"]
  insteadOf = https://github.com/
```

* --offline: The new tool doesn't maintain a git cache so we don't have the
  option to use locally cached repositories.
* --no-requirements
* --insecure

</span><br>

### Configuring an Mbed program

<span style="background-color:green;color:black">The subcommand "mbed-tools
configure" generates an Mbed OS config CMake file named "mbed_config.cmake" in
the path `cmake_build/<TARGET_NAME>/\<PROFILE>/\<TOOLCHAIN>/`.</span><br>

### Compiling an Mbed program

<span style="background-color:red;color:black">The subcommand "mbed-tools
compile" can be used to compile the program. The command-line-option "mbed
compile --source" is deprecated. To control which libraries and directories you
want to build either modify your application's "CMakeLists.txt" to add/exclude
or use `cmake --build cmake_build --target <library_name> --target
<other_library_name>` to add any number of targets to your build.</span><br>

<span style="background-color:red;color:black">The command-line-option "mbed
compile --library" is deprecated. Use standard CMake `add_library()`
instead.</span><br>

<span style="background-color:red;color:black">The command-line-option "mbed
compile -D MACRO_NAME" is deprecated. Use "mbed-tools configure" followed by
"cmake --build cmake_build -D MACRO_NAME" or `target_compile_definitions()` in
application "CMakeLists.txt".</span><br>

<span style="background-color:orange;color:black">The command-line-option "mbed
compile --build" will be supported at later point of time. Although we don't
currently have the option to explicitly state the build path, we have an ticket
open to track the issue
[#184](https://github.com/ARMmbed/mbed-tools/issues/184).</span><br>

### Testing an Mbed program

<span style="background-color:orange;color:black">The subcommand "mbed test"
will be supported at later point of time.</span><br>
