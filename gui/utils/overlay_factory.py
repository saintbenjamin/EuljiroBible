# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/overlay_factory.py
Provides a factory function to instantiate the WidgetOverlay using
current settings and display geometry.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

def create_overlay(settings, geometry, parent=None):
    """
    Creates an WidgetOverlay instance using the provided settings and screen geometry.

    Args:
        settings (dict): Settings dictionary containing overlay style configurations.
        geometry (QRect): Geometry of the screen on which to display the overlay.
        parent (QWidget, optional): Optional parent widget for the overlay.

    Returns:
        WidgetOverlay: A fully configured and ready-to-show overlay widget.
    """
    from gui.ui.widget_overlay import WidgetOverlay

    return WidgetOverlay(
        font_family=settings.get("display_font_family", "Arial"),
        font_size=int(settings.get("display_font_size", 36)),
        text_color=settings.get("display_text_color", "#000000"),
        bg_color=settings.get("display_bg_color", "#FFFFFF"),
        alpha=settings.get("display_bg_alpha", 0.85),
        mode=settings.get("display_overlay_mode", "fullscreen"),
        geometry=geometry,
        parent=parent
    )