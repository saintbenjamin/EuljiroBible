# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/ui_restore.py
Restores user settings into the main window UI components.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

def restore_settings_to_ui(win, settings):
    """
    Applies saved settings to the main window's UI components.

    Args:
        win (MainWindow): The main window instance.
        settings (dict): Loaded user settings.
    """
    try:
        # --- Restore TabVerse ---
        tab_verse = win.tabs.widget(0)

        # Book, Chapter, Verse fields
        tab_verse.book_combo.setCurrentText(settings.get("last_book", "Genesis"))
        tab_verse.chapter_input.setCurrentText(str(settings.get("last_chapter", 1)))
        tab_verse.verse_input.setText(settings.get("last_verse", "1"))

        # Checkboxes: bold, shadow, color
        if hasattr(tab_verse, "cb_bold"):
            tab_verse.cb_bold.setChecked(settings.get("bold_enabled", False))
        if hasattr(tab_verse, "cb_shadow"):
            tab_verse.cb_shadow.setChecked(settings.get("shadow_enabled", False))
        if hasattr(tab_verse, "cb_color"):
            tab_verse.cb_color.setChecked(settings.get("color_enabled", True))

        # Additional tabs or UI restoration can be added here later

    except Exception as e:
        print("[ERROR] Failed to restore UI settings:", e)