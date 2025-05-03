# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/utils_window.py
Provides helper functions to find the main window instance in the EuljiroBible GUI.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtWidgets import QApplication
from gui.ui.window_main import WindowMain

def find_window_main(widget):
    """
    Recursively finds the main application window starting from a given widget.

    Args:
        widget (QWidget): Any child widget in the UI hierarchy.

    Returns:
        WindowMain | None: The top-level WindowMain instance or None if not found.
    """
    parent = widget
    while parent is not None:
        if isinstance(parent, WindowMain):
            return parent
        parent = parent.parent()
    return None