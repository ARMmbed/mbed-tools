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
# Sources a pre-compiled GCC installation from AWS, installing the archive by
#  extracting and prepending the executable directory to PATH.
# Ccache is enabled for `arm-none-eabi-`.
#
# Note: Expects 'deps_url' and 'deps_dir' to already be defined.
#
_setup_build_env()
{
  # Enable Ccache in Travis
  ccache -o compiler_check=content
  ccache -M 1G
  pushd /usr/lib/ccache
  sudo ln -s ../../bin/ccache arm-none-eabi-gcc
  sudo ln -s ../../bin/ccache arm-none-eabi-g++
  export "PATH=/usr/lib/ccache:${PATH}"
  popd

  # Ignore shellcheck warnings: Variables defined in .travis.yml
  # shellcheck disable=SC2154
  local url="${deps_url}/gcc9-linux.tar.bz2"

  # shellcheck disable=SC2154
  local gcc_path="${deps_dir}/gcc/gcc-arm-none-eabi-9-2019-q4-major"

  local archive="gcc.tar.bz2"

  info "URL: ${url}"

  if [ ! -d "${deps_dir}/gcc" ]; then

    info "Downloading archive"
    curl --location "${url}" --output "${deps_dir}/${archive}"
    ls -al "${deps_dir}"

    info "Extracting 'gcc'"
    mkdir -p "${deps_dir}/gcc"
    tar -xf "${deps_dir}/${archive}" -C "${deps_dir}/gcc"
    rm "${deps_dir}/${archive}"

  fi

  info "Installing 'gcc'"
  export "PATH=${PATH}:${gcc_path}/bin"

  arm-none-eabi-gcc --version
  pip install --upgrade cmake
}

_config_and_build()
{
    mbedtools configure -t GCC_ARM -m ${TARGET_NAME}

    cmake -S . -B build -GNinja -DCMAKE_BUILD_TYPE=${PROFILE}
    cmake --build build
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
