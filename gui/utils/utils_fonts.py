# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/utils_fonts.py
Provides utility functions for managing fonts across the GUI and overlay in EuljiroBible.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
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
    Creates a QFont instance with the given settings.
    Converts int weight to QFont.Weight safely.

    Args:
        family (str): Font family name (e.g., "Noto Sans").
        size (int): Font point size.
        weight_value (int): Integer weight value (e.g., 50, 75).

    Returns:
        QFont: Configured QFont instance.
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
    Loads saved font settings from settings file and applies to QApplication.

    If loading fails, a fallback font is applied and exception is logged.
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
    Recursively applies the given font to the specified widget and all its child widgets.

    Args:
        widget (QWidget): The root widget to apply the font to.
        font (QFont): The font to apply.
    """
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)

def apply_main_font_to_app(font_family, font_size, font_weight, root_widget):
    """
    Applies the main font settings to the QApplication and all children of the given root widget.

    Args:
        font_family (str): Font family name.
        font_size (int): Font size.
        font_weight (QFont.Weight): Font weight enum.
        root_widget (QWidget): Root widget to apply font recursively.
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
    Applies font settings to the overlay widget and re-applies overlay styles.

    Args:
        widget_overlay (WidgetOverlay): The overlay instance.
        settings (dict): Dictionary with keys: display_font_family, display_font_size, display_font_weight
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