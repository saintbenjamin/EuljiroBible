# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/launch.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Launches the EuljiroBible application by initializing settings and opening the main window.
"""

import os
import platform
from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QFont, QIcon, QPalette

from core.utils.bible_data_loader import BibleDataLoader
from core.utils.utils_version import refresh_full_version_list
from gui.config.config_manager import ConfigManager
from gui.utils.utils_theme import set_dark_mode
from gui.utils.state_saver import save_settings_from_ui

def launch(app, saved_versions, settings, app_version):
    """
    Launch and initialize the main EuljiroBible GUI window.

    This function performs the full startup sequence:

    - Builds the full Bible version list for UI display.
    - Lazily loads Bible data for the last-used version set.
    - Applies platform-specific app icon.
    - Applies theme (dark/light) based on user setting, with an auto fallback.
    - Applies application-wide font settings.
    - Creates and shows :class:`gui.ui.window_main.WindowMain`.
    - Restores language and last UI state (versions, book/chapter/verse).
    - Finalizes selection summary and persists the restored state.

    Args:
        app (QApplication):
            The running QApplication instance.
        saved_versions (list[str] | None):
            Previously selected version identifiers (may be ignored if
            `settings["last_versions"]` exists).
        settings (dict):
            Application settings dictionary loaded from disk.
        app_version (str):
            Application version string (for window title/about display).

    Returns:
        WindowMain:
            The initialized main window instance.
    """
    from gui.ui.window_main import WindowMain

    # Get all version strings from actual data files
    version_list = refresh_full_version_list()
    available_versions = set(version_list)

    saved_versions = [
        version for version in settings.get("last_versions", [])
        if version in available_versions
    ]
    if not saved_versions and version_list:
        saved_versions = [version_list[0]]

    # Load only versions used last session (lazy load)
    bible_loader = BibleDataLoader()
    bible_loader.load_versions(saved_versions)

    # Set platform-specific icon (ICO for Windows, SVG otherwise)
    if platform.system() == "Windows":
        icon_filename = "thepck.ico"
    else:
        icon_filename = "thepck.svg"

    icon_path = os.path.join(ConfigManager.get_icon_dir(), icon_filename)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Determine if dark mode should be enabled
    auto_dark = app.palette().color(QPalette.Window).lightness() < 128
    user_pref = settings.get("dark_mode")
    effective_dark = user_pref if user_pref is not None else auto_dark
    set_dark_mode(app, effective_dark)

    # Apply application-wide font settings
    font_family = settings.get("font_family", ConfigManager.get_default_font())
    font_size = settings.get("font_size", 12)
    font = QFont(font_family, font_size)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    # Create main window instance
    win = WindowMain(version_list, settings, icon_path, app_version)
    tab_verse = win.tabs.widget(0)

    # Prevent change-triggered side effects during startup
    tab_verse.initializing = True

    win.show()

    # Restore language setting
    lang_code = settings.get("last_language", "ko")
    win.change_language(lang_code)

    # Restore last selected book if any
    saved_book = settings.get("last_book", "")
    first_checked_item = None

    # Restore checked Bible versions in UI
    for i in range(tab_verse.version_layout.count()):
        widget = tab_verse.version_layout.itemAt(i).widget()
        if isinstance(widget, QCheckBox):
            widget.blockSignals(True)
            is_checked = getattr(widget, "version_key", widget.text()) in saved_versions
            widget.setChecked(is_checked)
            widget.blockSignals(False)
            if is_checked and first_checked_item is None:
                first_checked_item = widget

    # Restore last selected book/chapter/verse if present
    if saved_book:
        display_name = win.tab_verse.bible_data.get_standard_book(saved_book, win.current_language)
        win.tab_verse.book_combo.setCurrentText(display_name)
        win.tab_verse.book_combo.lineEdit().setText(display_name)
    else:
        win.tab_verse.book_combo.setCurrentIndex(0)

    tab_verse.chapter_input.setCurrentText(str(settings.get("last_chapter", 1)))
    tab_verse.verse_input.setText(settings.get("last_verse", ""))

    # Allow change-tracking again
    tab_verse.initializing = False
    tab_verse.selection_manager.update_version_summary(tab_verse)

    # Save all current UI state (font, selection, version, etc.)
    save_settings_from_ui(app, tab_verse)

    return win
