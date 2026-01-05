# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/core/config/paths.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

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
"""

import os
import sys
import platform

# ───── Base and resource directories ─────
#: Absolute path to the project root directory.
#:
#: This path is resolved differently depending on the execution context:
#:
#: - When running as a frozen PyInstaller executable, this is set to the
#:   directory containing the executable.
#: - When running from source (CLI or GUI), this is dynamically determined
#:   by traversing upward from the current file location until a directory
#:   containing ``core/`` is found.
#:
#: All other project paths are derived from this base directory.
BASE_DIR = None

#: Base directory for bundled resources.
#:
#: When frozen (PyInstaller), this points to the extracted resource
#: directory (``sys._MEIPASS``). Otherwise, it is the same as ``BASE_DIR``.
RESOURCE_DIR = None

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

#: Icon resource directory.
#:
#: On Windows, this uses ``.../gui/resources/icons`` (``.ico`` files).
#: On other systems, it uses ``.../gui/resources/svg`` (``.svg`` files).
ICON_DIR = os.path.join(
    RESOURCE_DIR, "gui", "resources",
    "icons" if platform.system() == "Windows" else "svg"
)

# ───── Project data and JSON directories ─────
#: Directory containing Bible version JSON data files (typically ``data/``).
BIBLE_DATA_DIR = os.path.join(BASE_DIR, "data")

#: Directory containing JSON configs and settings (typically ``json/``).
JSON_DIR = os.path.join(BASE_DIR, "json")

#: Directory containing Bible name/version alias JSON files
#: (typically ``json/bible/``).
BIBLE_NAME_DIR = os.path.join(JSON_DIR, "bible")

#: Directory containing translation JSON files
#: (typically ``json/translations/``).
TRANSLATION_DIR = os.path.join(JSON_DIR, "translations")

# ───── Icon file ─────
#: Application icon file path.
#:
#: On Windows, this is typically ``thepck.ico``; on other systems,
#: ``thepck.svg``.
ICON_FILE = os.path.join(
    ICON_DIR,
    "thepck.ico" if platform.system() == "Windows" else "thepck.svg"
)

# ───── Logs and settings ─────
#: Main application settings JSON file (typically ``json/settings.json``).
SETTINGS_FILE = os.path.join(JSON_DIR, "settings.json")

#: Runtime error log file path (typically ``BASE_DIR/error_log.txt``).
LOG_FILE = os.path.join(BASE_DIR, "error_log.txt")

#: Memory diagnostics log file path
#: (typically ``BASE_DIR/memory_log.txt``).
MEMORY_LOG_FILE = os.path.join(BASE_DIR, "memory_log.txt")

# ───── Bible alias/config files ─────
#: GUI Bible version alias mapping JSON file.
ALIASES_VERSION_FILE = os.path.join(BIBLE_NAME_DIR, "aliases_version.json")

#: CLI Bible version alias mapping JSON file
#: (simplified aliases for CLI parsing).
ALIASES_VERSION_CLI_FILE = os.path.join(BIBLE_NAME_DIR, "aliases_version_cli.json")

#: Book name alias mapping JSON file.
ALIASES_BOOK_FILE = os.path.join(BIBLE_NAME_DIR, "aliases_book.json")

#: Canonical book list JSON file used as the standard reference.
STANDARD_BOOK_FILE = os.path.join(BIBLE_NAME_DIR, "standard_book.json")

#: Custom book sort order JSON file.
SORT_ORDER_FILE = os.path.join(BIBLE_NAME_DIR, "your_sort_order.json")