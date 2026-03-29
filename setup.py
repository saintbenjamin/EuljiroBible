# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/setup.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:License: MIT License with Attribution Requirement (see LICENSE file for details)

Legacy compatibility setup script for EuljiroBible.

# Description
This file exists solely to provide backward compatibility with older
Python packaging environments (e.g., pip < 21) that do not support
PEP 660 editable installs via ``pyproject.toml``.

Modern environments will ignore this file and rely on ``pyproject.toml``.
Older environments will fall back to this script for installation.

# Notes
- This file should remain minimal and in sync with ``pyproject.toml``.
- Do not introduce logic here unless strictly necessary.
- This is a compatibility layer, not the primary build configuration.
"""

from setuptools import setup

setup(
    name="EuljiroBible",
    version="2.1.7",
    description="Command-line Bible search tool with multi-version support",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Benjamin Jaedon Choi",
    author_email="euljirochurch@gmail.com",
    license="MIT",
    python_requires=">=3.8",
    packages=["cli", "core"],
    entry_points={
        "console_scripts": [
            "bible=cli.cli_main:main",
        ],
    },
    include_package_data=True,
)
