#!/bin/bash -euf
##
## Copyright (C) 2020 Arm Mbed. All rights reserved.
## SPDX-License-Identifier: Apache-2.0
##

set -o pipefail


#
# Helper functions for printing status information.
#  Uses 'echo' instead of 'printf' due to Travis CI stdout sync issues.
#
info() { echo -e "I: ${1}"; }

#
# Set up a development environment suitable for running our tests
#
_setup_build_env()
{
  # Enable ccache for `arm-none-eabi-` and all other default toolchains.
  ccache -o compiler_check=content
  ccache -M 1G
  pushd /usr/local/opt/ccache/libexec
  sudo ln -s ../bin/ccache arm-none-eabi-gcc
  sudo ln -s ../bin/ccache arm-none-eabi-g++
  export "PATH=/usr/local/opt/ccache/libexec:${PATH}:"
  popd

  arm-none-eabi-gcc --version
  cmake --version
}

_clone_dependencies()
{
  # We use manual clone, with depth and single branch = the fastest
  git clone --depth=1 --single-branch --branch feature-cmake https://github.com/ARMmbed/${EXAMPLE_NAME}.git

  if [ -z ${SUBEXAMPLE_NAME} ]; then
      cd ${EXAMPLE_NAME}
  else
      cd ${EXAMPLE_NAME}/${SUBEXAMPLE_NAME}
  fi

  git clone --depth=1 --single-branch --branch feature-cmake https://github.com/ARMmbed/mbed-os.git

  echo “” > mbed-os.lib

  mbedtools checkout
}
