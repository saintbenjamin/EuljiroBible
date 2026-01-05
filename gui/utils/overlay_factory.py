# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/overlay_factory.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Provides a factory function to instantiate the WidgetOverlay using
current settings and display geometry.
"""

def create_overlay(settings, geometry, parent=None):
    """
    Create and return a configured overlay widget instance.

    This factory function constructs a `WidgetOverlay` using the current
    overlay-related settings and the target screen geometry. It centralizes
    overlay creation logic so that callers do not need to manually extract
    individual style parameters from the settings dictionary.

    Args:
        settings (dict): Application settings dictionary containing overlay-related keys,
            such as font family, font size, colors, transparency, and display mode.
        geometry (QRect): Screen geometry defining the initial size and position
            of the overlay window.
        parent (QWidget | None): Optional parent widget for ownership and stacking context.

    Returns:
        WidgetOverlay: A fully initialized overlay widget ready to be shown.
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