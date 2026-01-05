# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/constants/messages.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Centralized error message constants for user-facing dialogs in EuljiroBible.
Intended for reuse across GUI modules to maintain consistency and easy localization.
"""

# ───── Error message constants ─────
#: Centralized dictionary of user-facing error and warning messages used
#: throughout the EuljiroBible GUI.
#:
#: This mapping is intended to:
#:
#: - Ensure consistent wording and tone across all dialogs and message boxes
#: - Avoid hard-coded strings scattered across GUI modules
#: - Serve as a single point of modification for future localization (i18n)
#: - Separate presentation text from application logic
#:
#: Each key represents a semantic error or warning condition, while the
#: corresponding value is the message string shown to the user.
#:
#: Some messages support runtime formatting via ``str.format`` (e.g. ``{path}``).
#:
#: Typical usage::
#:
#:     from gui.constants.messages import ERROR_MESSAGES
#:     msg = ERROR_MESSAGES["settings_load"]
#:
#: Defined messages include (non-exhaustive):
#:
#: - ``pyside6_missing``:
#:   Displayed when PySide6 is not installed and the GUI cannot be started.
#:
#: - ``wsl_display``:
#:   Shown when running under WSL without a configured X server or DISPLAY.
#:
#: - ``settings_load`` / ``settings_save``:
#:   Warnings related to loading or saving application settings.
#:
#: - ``critical_error``:
#:   Generic fatal error message directing the user to the error log file.
#:
#: - ``bible_data_missing``:
#:   Error raised when the Bible data directory does not exist.
#:
#: - ``bible_files_missing``:
#:   Error raised when no Bible JSON files are found in the expected directory.
#:
#: - ``POLL_INTERVAL_INVALID_TITLE`` / ``POLL_INTERVAL_INVALID_MSG``:
#:   Title and body strings used for polling interval input validation dialogs.
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