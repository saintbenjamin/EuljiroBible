# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/config/paths.py

Centralizes and defines file and directory paths used throughout the EuljiroBible project.

This module handles resource resolution regardless of whether the app is run from source
or as a frozen PyInstaller executable. It provides standardized access to Bible data files,
icon files, JSON configuration files, language translation files, logs, and settings.

Usage scenarios include:
    - Loading Bible text and name metadata
    - Locating translation JSON files for GUI language switching
    - Resolving the appropriate application icon per platform
    - Saving and loading user settings
    - Logging runtime errors and memory diagnostics

Platform-aware behaviors:
    - On Windows, selects `.ico` icons; on other systems, `.svg`
    - Dynamically computes `BASE_DIR` based on the runtime context

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import os
import sys
import platform

# Determine BASE_DIR depending on execution context
if getattr(sys, 'frozen', False):
    # Case 1: PyInstaller-built executable
    BASE_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = sys._MEIPASS
else:
    # Case 2: Source or editable install (CLI or GUI)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Climb up until project root is found (has 'core/' inside it)
    while not os.path.isdir(os.path.join(BASE_DIR, "core")):
        parent = os.path.dirname(BASE_DIR)
        if parent == BASE_DIR:
            break  # Reached root → give up
        BASE_DIR = parent

    RESOURCE_DIR = BASE_DIR

# Determine the icon resource directory
ICON_DIR = os.path.join(
    RESOURCE_DIR, "gui", "resources",
    "icons" if platform.system() == "Windows" else "svg"
)

# Paths to various project resource folders and files
BIBLE_DATA_DIR = os.path.join(BASE_DIR, "data")
JSON_DIR = os.path.join(BASE_DIR, "json")
BIBLE_NAME_DIR = os.path.join(JSON_DIR, "bible")
TRANSLATION_DIR = os.path.join(JSON_DIR, "translations")

ICON_FILE = os.path.join(
    ICON_DIR,
    "thepck.ico" if platform.system() == "Windows" else "thepck.svg"
)
SETTINGS_FILE = os.path.join(JSON_DIR, "settings.json")
LOG_FILE = os.path.join(BASE_DIR, "error_log.txt")
MEMORY_LOG_FILE = os.path.join(BASE_DIR, "memory_log.txt")

# Bible version and book alias mapping files
ALIASES_VERSION_FILE = os.path.join(BIBLE_NAME_DIR, "aliases_version.json")
ALIASES_VERSION_CLI_FILE = os.path.join(BIBLE_NAME_DIR, "aliases_version_cli.json")
ALIASES_BOOK_FILE = os.path.join(BIBLE_NAME_DIR, "aliases_book.json")
STANDARD_BOOK_FILE = os.path.join(BIBLE_NAME_DIR, "standard_book.json")
SORT_ORDER_FILE = os.path.join(BIBLE_NAME_DIR, "your_sort_order.json")