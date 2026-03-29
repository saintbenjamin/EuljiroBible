# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/utils_display.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Provides utility functions for listing display screen descriptions in EuljiroBible.
"""

from PySide6.QtWidgets import QApplication

def get_display_descriptions():
    """
    Return human-readable descriptions of all connected displays.

    Each entry includes:

    - Display index (1-based)
    - Screen resolution (width × height)
    - Top-left screen position in virtual desktop coordinates

    This helper is typically used to populate display-selection dropdowns
    for overlay or presentation output configuration.

    Returns:
        List[str]: Display descriptions in the format
            "Display N: WxH @ (X,Y)".
    """
    return [
        f"Display {i+1}: {geo.width()}x{geo.height()} @ ({geo.x()},{geo.y()})"
        for i, screen in enumerate(QApplication.screens())
        for geo in [screen.geometry()]
    ]