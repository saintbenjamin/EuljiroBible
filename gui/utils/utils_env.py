# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/utils_env.py
Configures and validates environment settings required for GUI display (e.g. WSL compatibility).

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import sys, os
import platform
from gui.constants import messages
from gui.utils.logger import handle_exception
from core.utils.logger import log_debug

def setup_environment():
    """
    Sets Qt environment variables for scaling on HiDPI or fractional displays.
    """
    os.environ["QT_SCALE_FACTOR"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

def verify_wsl_display():
    """
    Ensures DISPLAY environment variable is set when running under WSL.
    Exits the app with a user-friendly message if not configured correctly.
    """
    if "microsoft" in platform.uname().release.lower() and not os.environ.get("DISPLAY"):
        log_debug('Checking DISPLAY environment for WSL.')
        msg = messages.ERROR_MESSAGES["wsl_display"]
        handle_exception(None, "WSL DISPLAY Error", msg)
        sys.exit(1)