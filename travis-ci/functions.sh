#!/bin/bash -euf
#
# Copyright (c) 2020 Arm Limited. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
_install_gcc_and_ccache()
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
}
