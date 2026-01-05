# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/utils_fonts.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Provides utility functions for managing fonts across the GUI and overlay in EuljiroBible.
"""

import json
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QApplication

from core.config import paths
from gui.constants import messages
from gui.utils.logger import handle_exception
from gui.config.config_manager import ConfigManager

def create_app_font(family: str, size: int, weight_value: int) -> QFont:
    """
    Create a QFont instance from the given font configuration.

    This helper converts an integer weight into a ``QFont.Weight`` safely,
    falling back to ``QFont.Weight.Normal`` if the value is invalid.

    Args:
        family (str): Font family name (e.g., ``"Noto Sans"``).
        size (int): Font point size.
        weight_value (int): Integer weight value compatible with ``QFont.Weight``
            (e.g., ``50``, ``75``).

    Returns:
        QFont: Configured font instance with antialias preference enabled.
    """
    font = QFont(family, size)
    font.setStyleStrategy(QFont.PreferAntialias)

    try:
        font.setWeight(QFont.Weight(weight_value))
    except (ValueError, TypeError):
        font.setWeight(QFont.Weight.Normal)

    return font

def load_application_settings(app):
    """
    Load persisted application font settings and apply them to QApplication.

    This function reads the settings JSON file and applies the saved font family,
    size, and weight to the given ``QApplication`` instance.

    Failure behavior:
    - If loading or parsing fails, a GUI-safe error dialog is shown via
      ``handle_exception`` and the application continues (Qt default font remains).

    Args:
        app (QApplication): The QApplication instance to configure.

    Returns:
        None
    """
    try:
        with open(paths.SETTINGS_FILE, encoding="utf-8") as f:
            settings = json.load(f)
            font_family = settings.get("font_family", "Noto Sans")
            font_size = settings.get("font_size", 12)
            font_weight = settings.get("font_weight", QFont.Weight.Normal)
            font = create_app_font(font_family, font_size, font_weight)
            app.setFont(font)

    except Exception as e:
        handle_exception(e, "Settings Load Error", messages.ERROR_MESSAGES["settings_load"])

def apply_font_to_children(widget, font):
    """
    Apply a font recursively to a widget and all of its descendants.

    This is used to ensure consistent font appearance across widgets that do not
    automatically update after ``QApplication.setFont()`` on some platforms.

    Args:
        widget (QWidget): Root widget to apply the font to.
        font (QFont): Font to apply.

    Returns:
        None
    """
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)

def apply_main_font_to_app(font_family, font_size, font_weight, root_widget):
    """
    Persist and apply the main UI font across the application.

    This function:
    - Persists the font configuration via ``ConfigManager.save_font``.
    - Updates the global QApplication font.
    - Recursively applies the font to all children of ``root_widget``.

    Args:
        font_family (str): Font family name.
        font_size (int): Font point size.
        font_weight (QFont.Weight | int): Font weight. Expected to be compatible
            with ``QFont.setWeight()``.
        root_widget (QWidget): Root widget whose descendants should receive the font.

    Returns:
        None
    """
    ConfigManager.save_font(font_family, font_size, font_weight)
    font = QApplication.font()
    font.setFamily(font_family)
    font.setPointSize(font_size)
    font.setWeight(font_weight)
    QApplication.setFont(font)
    apply_font_to_children(root_widget, font)

def apply_overlay_font(widget_overlay, settings):
    """
    Apply overlay font settings to an existing overlay widget.

    Note:
        ``WidgetOverlay.apply_settings()`` already reads from configuration and
        applies font + colors + sizing logic. This helper sets a base font first
        and then delegates the full refresh to ``apply_settings()``.

    Args:
        widget_overlay (WidgetOverlay | None): Overlay instance to update.
        settings (dict): Settings dictionary expected to contain:
            - ``display_font_family`` (str)
            - ``display_font_size`` (int)
            - ``display_font_weight`` (int or QFont.Weight)

    Returns:
        None
    """
    if not widget_overlay:
        return

    font = QFont(
        settings.get("display_font_family", "Arial"),
        int(settings.get("display_font_size", 36))
    )
    font.setWeight(settings.get("display_font_weight", QFont.Weight.Normal))
    widget_overlay.setFont(font)
    widget_overlay.apply_settings()