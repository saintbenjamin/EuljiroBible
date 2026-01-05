# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/utils_env.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Configures and validates environment settings required for GUI display (e.g. WSL compatibility).
"""

import sys, os
import platform
from gui.constants import messages
from gui.utils.logger import handle_exception
from core.utils.logger import log_debug

def setup_environment():
    """
    Configure Qt-related environment variables for display scaling.

    This function sets explicit Qt environment variables to ensure predictable
    behavior on HiDPI or fractional-scaling displays. It is intended to be called
    early in application startup, before creating the QApplication instance.

    Effects:
        - Disables implicit scale-factor guessing by Qt.
        - Forces consistent scaling behavior across platforms.

    Returns:
        None
    """
    os.environ["QT_SCALE_FACTOR"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

def verify_wsl_display():
    """
    Verify DISPLAY environment configuration when running under WSL.

    On Windows Subsystem for Linux (WSL), a valid X server and DISPLAY variable
    are required to launch Qt GUI applications. This function detects a WSL
    environment and terminates the application with a user-friendly error dialog
    if DISPLAY is not configured.

    Behavior:
        - Detects WSL via kernel release string.
        - Shows a localized error message using the GUI error handler.
        - Exits the application with a non-zero status on failure.

    Returns:
        None

    Raises:
        SystemExit: If DISPLAY is missing under WSL.
    """
    if "microsoft" in platform.uname().release.lower() and not os.environ.get("DISPLAY"):
        log_debug('Checking DISPLAY environment for WSL.')
        msg = messages.ERROR_MESSAGES["wsl_display"]
        handle_exception(None, "WSL DISPLAY Error", msg)
        sys.exit(1)