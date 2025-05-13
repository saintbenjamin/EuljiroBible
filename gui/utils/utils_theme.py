# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/utils_theme.py
Handles theme switching and dynamic layout refresh for EuljiroBible GUI components.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import qdarkstyle

def set_dark_mode(app, enable: bool):
    """
    Applies or removes the application's dark theme.

    Args:
        app (QApplication): QApplication instance.
        enable (bool): True to apply dark theme, False to revert.
    """
    if enable:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
    else:
        app.setStyleSheet("")