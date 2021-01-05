#
# Copyright (c) 2020-2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Package definition for PyPI."""
import os

from setuptools import setup, find_packages

PROJECT_SLUG = "mbed-tools"
SOURCE_DIR = "src/mbed_tools"

repository_dir = os.path.dirname(__file__)

# Use readme needed as long description in PyPI
with open(os.path.join(repository_dir, "README.md"), encoding="utf8") as fh:
    long_description = fh.read()

setup(
    author="Mbed team",
    author_email="support@mbed.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Embedded Systems",
    ],
    description="Command line interface for Mbed OS.",
    keywords="Arm Mbed OS MbedOS cli command line tools",
    include_package_data=True,
    install_requires=[
        "python-dotenv",
        "Click==7.1",
        "pdoc3",
        "GitPython",
        "tqdm",
        "tabulate",
        "dataclasses; python_version<'3.7'",
        "requests>=2.20",
        "pywin32; platform_system=='Windows'",
        "psutil; platform_system=='Linux'",
        "pyudev; platform_system=='Linux'",
        "typing-extensions",
        "Jinja2",
        "pyserial",
    ],
    license="Apache 2.0",
    long_description_content_type="text/markdown",
    long_description=long_description,
    name=PROJECT_SLUG,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6,<4",
    url=f"https://github.com/ARMmbed/{PROJECT_SLUG}",
    entry_points={
        "console_scripts": [
            "mbedtools=mbed_tools.cli.main:cli",
            "mbed-tools=mbed_tools.cli.main:cli",
            "mbed_tools=mbed_tools.cli.main:cli",
        ]
    },
)
