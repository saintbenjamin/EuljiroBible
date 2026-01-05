# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/utils_dialog.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Provides helper functions for GUI dialogs such as color selection and file save location.
"""

from PySide6.QtWidgets import QFileDialog, QColorDialog
from gui.config.config_manager import ConfigManager

def set_color_from_dialog(button, setting_key, callback=None):
    """
    Open a color picker dialog and apply the selected color to a button and settings.

    This utility:

    - Opens a QColorDialog for user selection.
    - Updates the button background to reflect the chosen color.
    - Persists the color value to settings via ConfigManager.
    - Optionally triggers a callback (commonly used to reapply dynamic settings).

    Args:
        button (QPushButton): Button whose background color represents the setting.
        setting_key (str): Settings key to update with the selected color value.
        callback (Callable | None): Optional function to invoke after applying the color.

    Returns:
        None
    """
    color = QColorDialog.getColor()
    if color.isValid():
        button.setStyleSheet(f"background-color: {color.name()}")
        ConfigManager.update_partial({setting_key: color.name()})
        if callback:
            callback()

def get_save_path(parent, current_path, title, file_filter="Text Files (*.txt)"):
    """
    Open a file-save dialog and return the selected path.

    This helper wraps QFileDialog.getSaveFileName() and is used to select
    output paths such as verse_output.txt.

    Args:
        parent (QWidget): Parent widget for the file dialog.
        current_path (str): Initial path shown in the dialog.
        title (str): Dialog window title.
        file_filter (str): File type filter string (Qt format).

    Returns:
        str: Selected file path, or an empty string if the dialog was cancelled.
    """
    path, _ = QFileDialog.getSaveFileName(parent, title, current_path, file_filter)
    return path