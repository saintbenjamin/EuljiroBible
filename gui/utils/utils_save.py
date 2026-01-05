# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/utils_save.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Handles saving of user settings from the GUI state at exit.
"""

from core.utils.logger import log_debug
from gui.config.config_manager import ConfigManager
from gui.constants import messages
from gui.utils.logger import handle_exception

def save_user_settings(app, win):
    """
    Persist user settings when the GUI application exits.

    This function collects relevant runtime UI state from the main window and
    writes it to the settings store. It is typically invoked during application
    shutdown to ensure that the next launch restores the user’s most recent context.

    Captured settings include:

    - Application font family and size
    - Last selected Bible versions
    - Last selected book, chapter, and verse
    - Current dark mode state

    Args:
        app (QApplication): Active QApplication instance used to query global font
            and theme (dark mode) state.
        win (QMainWindow): Main application window containing the tab widgets
            and verse-selection UI.

    Returns:
        None
    """
    if not win:
        return
    tab_verse = win.tabs.widget(0)
    selected_versions = tab_verse.version_helper.get_selected_versions()
    book_combo = tab_verse.book_combo
    chapter_input = tab_verse.chapter_input
    verse_input = tab_verse.verse_input

    try:
        current_settings = ConfigManager.load()
        current_settings.update({
            "font_family": app.font().family(),
            "font_size": app.font().pointSize(),
            "last_versions": selected_versions,
            "last_book": book_combo.currentText(),
            "last_chapter": int(chapter_input.currentText()) if chapter_input.currentText().isdigit() else 1,
            "last_verse": verse_input.text(),
            "dark_mode": bool(app.styleSheet())
        })
        ConfigManager.save(current_settings)
        log_debug(f'Settings saved: {current_settings}')
    except Exception as e:
        handle_exception(e, "Settings Save Error", messages.ERROR_MESSAGES["settings_save"])