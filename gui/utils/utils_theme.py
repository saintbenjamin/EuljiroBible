# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/utils_theme.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Handles theme switching and dynamic layout refresh for EuljiroBible GUI components.
"""

import qdarkstyle

def set_dark_mode(app, enable: bool):
    """
    Enable or disable the application-wide dark theme.

    This helper applies a Qt stylesheet for dark mode when enabled and
    restores the default (light) appearance when disabled. It operates
    directly on the QApplication instance.

    Args:
        app (QApplication): QApplication instance to which the theme is applied.
        enable (bool): If True, apply the dark theme; if False, clear the stylesheet
            and revert to the default theme.

    Returns:
        None
    """
    if enable:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
    else:
        app.setStyleSheet("")