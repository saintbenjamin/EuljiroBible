# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/settings_helper.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Provides helper functions for extracting and updating settings
based on user interface widget states, especially overlay-related UI components.
"""

def update_overlay_settings(settings, widget_overlays):
    """
    Collect overlay display settings from UI widgets and update the settings dictionary.

    This function reads the current state of overlay-related UI controls
    (font, size, weight, colors, transparency, and display mode) and writes
    their values into the provided settings dictionary using standardized keys.

    It is designed to be called whenever overlay UI controls change, ensuring
    that runtime behavior and persisted configuration remain consistent.

    Args:
        settings (dict): Application settings dictionary to update in-place.

        widget_overlays (dict): Mapping of overlay-related UI widgets.
            Expected keys and widget types:

                - "font_family_combo" (QComboBox | QFontComboBox):
                    Font family selector.
                - "font_size_combo" (QComboBox):
                    Font size selector (text convertible to int).
                - "font_weight_combo" (QComboBox):
                    Font weight selector (Qt weight stored as item data).
                - "alpha_slider" (QSlider):
                    Background transparency slider (0–100).
                - "text_color_btn" (QPushButton):
                    Button whose palette color represents text color.
                - "bg_color_btn" (QPushButton):
                    Button whose palette color represents background color.
                - "mode_combo" (QComboBox):
                    Overlay mode selector (index 0 = fullscreen, 1 = resizable).

    Returns:
        dict: The updated settings dictionary containing overlay display configuration.
    """
    font_family = widget_overlays["font_family_combo"].currentText()
    font_size = int(widget_overlays["font_size_combo"].currentText())
    font_weight = widget_overlays["font_weight_combo"].currentData()
    alpha = round(widget_overlays["alpha_slider"].value() / 100.0, 2)
    text_color = widget_overlays["text_color_btn"].palette().button().color().name()
    bg_color = widget_overlays["bg_color_btn"].palette().button().color().name()
    mode = "fullscreen" if widget_overlays["mode_combo"].currentIndex() == 0 else "resizable"

    settings.update({
        "display_font_family": font_family,
        "display_font_size": font_size,
        "display_font_weight": font_weight,
        "display_bg_alpha": alpha,
        "display_text_color": text_color,
        "display_bg_color": bg_color,
        "display_overlay_mode": mode
    })

    return settings