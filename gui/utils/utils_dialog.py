# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/utils_dialog.py
Provides helper functions for GUI dialogs such as color selection and file save location.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtWidgets import QFileDialog, QColorDialog
from gui.config.config_manager import ConfigManager

def set_color_from_dialog(button, setting_key, callback=None):
    """
    Opens QColorDialog, updates button color, saves to settings, and runs callback.

    Args:
        button (QPushButton): The button to update the background color of.
        setting_key (str): Settings dictionary key to update.
        callback (function, optional): Function to call after color is applied.
    """
    color = QColorDialog.getColor()
    if color.isValid():
        button.setStyleSheet(f"background-color: {color.name()}")
        ConfigManager.update_partial({setting_key: color.name()})
        if callback:
            callback()

def get_save_path(parent, current_path, title, file_filter="Text Files (*.txt)"):
    """
    Opens a file dialog and returns the selected save path.

    Args:
        parent (QWidget): Parent widget for dialog.
        current_path (str): Initial path.
        title (str): Dialog title.
        file_filter (str): File type filter string.

    Returns:
        str: Selected path or empty string if cancelled.
    """
    path, _ = QFileDialog.getSaveFileName(parent, title, current_path, file_filter)
    return path