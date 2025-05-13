# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/state_saver.py
Provides utility functions to save application settings from the UI state in EuljiroBible.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from gui.config.config_manager import ConfigManager

def save_settings_from_ui(app, tab_verse):
    """
    Saves UI state settings into the settings.json file.

    Captures font settings, last selected versions, last book/chapter/verse,
    and dark mode status from the UI and persists them.

    Args:
        app (QApplication): The main application instance.
        tab_verse (TabVerse): The verse tab widget containing the UI state.
    """
    selected_versions = tab_verse.version_helper.get_selected_versions()
    settings = {
        "font_family": app.font().family(),
        "font_size": app.font().pointSize(),
        "font_weight": app.font().weight(),
        "last_versions": selected_versions,
        "last_book": tab_verse.book_combo.currentText(),
        "last_chapter": int(tab_verse.chapter_input.currentText()) if tab_verse.chapter_input.currentText().isdigit() else 1,
        "last_verse": tab_verse.verse_input.text(),
        "dark_mode": bool(app.styleSheet())
    }
    ConfigManager.update_partial(settings)