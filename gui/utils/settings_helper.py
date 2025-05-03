# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/settings_helper.py
Provides helper functions for extracting and updating settings
based on user interface widget states, especially overlay-related UI components.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

def update_overlay_settings(settings, widget_overlays):
    """
    Updates the given settings dictionary with current values from overlay-related UI widgets.

    Args:
        settings (dict): The settings dictionary to be updated.
        widget_overlays (dict): A dictionary of UI widgets used for overlay settings.
            Expected keys:
                - "font_combo" (QComboBox or QFontComboBox): Font family selector
                - "size_combo" (QComboBox): Font size selector
                - "weight_combo" (QComboBox): Font weight selector
                - "alpha_slider" (QSlider): Background transparency slider
                - "text_color_btn" (QPushButton): Text color preview button
                - "bg_color_btn" (QPushButton): Background color preview button
                - "mode_combo" (QComboBox): Overlay mode selector ("fullscreen" or "resizable")

    Returns:
        dict: The updated settings dictionary with overlay display configurations.
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