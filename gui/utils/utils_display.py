# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/utils_display.py
Provides utility functions for listing display screen descriptions in EuljiroBible.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtWidgets import QApplication

def get_display_descriptions():
    """
    Returns a list of human-readable descriptions for all connected displays.

    Each description includes the display number, resolution, and position.

    Example:
        ["Display 1: 1920x1080 @ (0,0)", "Display 2: 1280x1024 @ (1920,0)"]

    Returns:
        list[str]: List of display descriptions in the format "Display N: WxH @ (X,Y)".
    """
    return [
        f"Display {i+1}: {geo.width()}x{geo.height()} @ ({geo.x()},{geo.y()})"
        for i, screen in enumerate(QApplication.screens())
        for geo in [screen.geometry()]
    ]