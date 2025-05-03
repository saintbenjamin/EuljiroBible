# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/constants/messages.py
Centralized error message constants for user-facing dialogs in EuljiroBible.
Intended for reuse across GUI modules to maintain consistency and easy localization.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

ERROR_MESSAGES = {
    "pyside6_missing": (
        "🚫 PySide6 is missing!\n\n"
        "Running from source?\n"
        "Get started:\n"
        "- Windows/Linux: pip install PySide6\n"
        "- macOS: brew install pyside"
    ),

    "wsl_display": (
        "🔺 An X server is required to use GUI in WSL (e.g., VcXsrv, X410).\n"
        "🔧 The DISPLAY environment variable is not set."
    ),

    "settings_load": "Failed to load settings. Using defaults.",
    "settings_save": "Failed to save settings.",
    "critical_error": "A fatal error occurred. See error_log.txt for details.",

    "bible_data_missing": "The Bible data directory ({path}) does not exist. The program will now exit.",
    "bible_files_missing": "No Bible data found in the json directory.\n{path}",

    # Polling input validation errors
    "POLL_INTERVAL_INVALID_TITLE": "Input error",
    "POLL_INTERVAL_INVALID_MSG": "Input proper integer."
}