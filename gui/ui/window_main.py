# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/window_main.py
Description: Defines the main application window for EuljiroBible, managing tabs, settings, language switching, overlay handling, and polling controls.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import platform

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, 
    QTabWidget, QLabel, QMessageBox, 
    QMenuBar, QMainWindow, QPushButton
)
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon

from gui.config.config_manager import ConfigManager
from gui.ui.locale.message_loader import get_available_languages, load_messages
from gui.ui.monitor_memory import MonitorMemory
from gui.ui.tab_verse import TabVerse
from gui.ui.tab_keyword import TabKeyword
from gui.ui.tab_settings import TabSettings

class WindowMain(QMainWindow):
    """
    Main application window class for EuljiroBible.

    Manages the main interface, including tabs for verse search, keyword search, settings,
    as well as language switching, overlay control, and polling behavior.
    """

    def __init__(self, version_list, settings, icon_path, app_version, parent=None):
        """
        Initializes the WindowMain.

        Args:
            version_list (list): List of available Bible versions.
            settings (dict): Loaded user settings.
            icon_path (str): Path to the application icon file.
        """
        super().__init__()

        self.settings = settings
        self.app_version = app_version

        self.current_language = "ko"
        self.messages = load_messages(self.current_language)
        self.setWindowTitle(self.tr("program_title").format(self.app_version))
        self.resize(900, 650)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        menubar = QMenuBar()
        self.help_menu = menubar.addMenu(self.tr("menu_help"))
        self.about_action = QAction(self.tr("menu_about"), self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)

        self.tools_menu = menubar.addMenu(self.tr("menu_tools"))
        self.memory_action = QAction(self.tr("menu_memory"), self)
        self.memory_action.triggered.connect(self.open_monitor_memory)
        self.tools_menu.addAction(self.memory_action)

        available_languages = get_available_languages()

        if available_languages:
            try:
                lang_messages = load_messages(self.current_language)
                menu_title = lang_messages.get("menu_lang", "언어 / Language")
            except Exception:
                menu_title = "언어 / Language"

            self.lang_menu = menubar.addMenu(menu_title)

            # Create a menu item for each available language
            # The lambda ensures lang_code is correctly captured in closure
            for lang_code in available_languages:
                try:
                    lang_messages = load_messages(lang_code)
                    display_name = lang_messages.get("language", lang_code.upper())
                except Exception:
                    display_name = lang_code.upper()

                action = QAction(display_name, self)
                action.triggered.connect(lambda checked=False, lc=lang_code: self.change_language(lc))
                self.lang_menu.addAction(action)

        self.test_error_action = QAction(self.tr("menu_test"), self)
        self.test_error_action.triggered.connect(self.trigger_error)

        self.tools_menu.addAction(self.test_error_action)

        self.setMenuBar(menubar)

        self.current_language = "ko"

        self.poll_toggle_btn = QPushButton()
        self.poll_toggle_btn.setCheckable(True)
        poll_enabled = self.settings.get("poll_enabled", False)
        self.poll_toggle_btn.setChecked(poll_enabled)
        self.update_poll_button_text()
        self.poll_toggle_btn.clicked.connect(self.on_poll_toggle_clicked)

        self.tabs = QTabWidget()
        self.tab_verse = TabVerse(
            version_list, 
            self.settings, 
            tr=self.tr,
            get_polling_status=lambda: self.poll_toggle_btn.isChecked(),
            get_always_show_setting=lambda: self.settings.get("always_show_on_off_buttons", False)
        )
        self.tabs.addTab(self.tab_verse, self.tr("tab_verse"))
        self.tab_keyword = TabKeyword(
            version_list, 
            self.settings, 
            tr=self.tr,
            get_polling_status=lambda: self.poll_toggle_btn.isChecked(),
            get_always_show_setting=lambda: self.settings.get("always_show_on_off_buttons", False)
        )
        self.tabs.addTab(self.tab_keyword, self.tr("tab_search"))
        self.tab_settings = TabSettings(
            app=QApplication.instance(), 
            settings=settings, 
            tr=self.tr, 
            get_poll_enabled_callback=lambda: self.poll_toggle_btn.isChecked(),
            get_main_geometry=self.frameGeometry,
            refresh_settings_callback=None
        )
        self.tab_settings.refresh_settings_callback = self.refresh_settings_and_tabs
        self.tab_settings.logic.refresh_settings_callback = self.refresh_settings_and_tabs

        self.tabs.addTab(self.tab_settings, self.tr("tab_font"))
        self.apply_tab_icons()

        self.tab_settings.apply_dynamic_settings()

        layout.addWidget(self.poll_toggle_btn)

        layout.addWidget(self.tabs)

        self.copyright_label = QLabel(self.tr("footer_copyright"))
        layout.addWidget(self.copyright_label)

        self.setCentralWidget(central_widget)

        self.tab_verse.update_button_layout()
        self.tab_keyword.update_button_visibility()
        self.tab_settings.update_presentation_visibility()     
        self.poll_toggle_btn.toggled.connect(self.tabs.widget(2).update_presentation_visibility)

    def tr(self, key):
        """
        Translates a UI key into the current language.

        Args:
            key (str): Translation key.

        Returns:
            str: Translated string.
        """
        return self.messages.get(key, key)

    def change_language(self, lang_code):
        """
        Changes the UI language dynamically.

        Args:
            lang_code (str): Language code (e.g., "ko", "en").
        """
        self.current_language = lang_code
        self.messages = load_messages(lang_code)

        self.setWindowTitle(self.tr("program_title").format(self.app_version))

        if not hasattr(self, "use_alias"):
            self.use_alias = False

        if hasattr(self, "alias_toggle_btn"):
            if self.use_alias:
                self.alias_toggle_btn.setText(self.tr("label_alias_short"))
            else:
                self.alias_toggle_btn.setText(self.tr("label_alias_full"))

        if hasattr(self, "help_menu"):
            self.help_menu.setTitle(self.tr("menu_help"))
        if hasattr(self, "tools_menu"):
            self.tools_menu.setTitle(self.tr("menu_tools"))
        if hasattr(self, "about_action"):
            self.about_action.setText(self.tr("menu_about"))
        if hasattr(self, "lang_menu"):
            self.lang_menu.setTitle(self.tr("menu_lang"))
        if hasattr(self, "memory_action"):
            self.memory_action.setText(self.tr("menu_memory"))
        if hasattr(self, "test_error_action"):
            self.test_error_action.setText(self.tr("menu_test"))

        if hasattr(self, "poll_toggle_btn"):
            self.update_poll_button_text()

        if hasattr(self, "tabs"):
            #icon = QIcon("resources/svg/tab_verse.svg")
            #self.tabs.setTabIcon(0, icon)
            self.tabs.setTabText(0, self.tr("tab_verse"))
            #icon = QIcon("resources/svg/tab_search.svg")
            #self.tabs.setTabIcon(1, icon)
            self.tabs.setTabText(1, self.tr("tab_search"))
            #icon = QIcon("resources/svg/tab_font.svg")
            #self.tabs.setTabIcon(2, icon)
            self.tabs.setTabText(2, self.tr("tab_font"))
            self.tabs.tabBar().setIconSize(QSize(30, 30))

            for i in range(self.tabs.count()):
                tab = self.tabs.widget(i)
                if hasattr(tab, "change_language"):
                    tab.change_language(lang_code)

        if hasattr(self, "copyright_label"):
            self.copyright_label.setText(self.tr("footer_copyright"))
        
        ConfigManager.update_partial({"last_language": lang_code})

    def refresh_settings_and_tabs(self):
        self.settings = ConfigManager.load()
        self.tab_verse.update_button_layout()
        self.tab_keyword.update_button_visibility()
        self.tab_settings.update_presentation_visibility()

    def apply_tab_icons(self):
        """
        Applies SVG icons to each tab in the tab widget, unless on macOS.

        On macOS, tab icons are skipped due to style inconsistencies in Qt rendering.
        """
        if platform.system() == "Darwin":
            return

        self.tabs.setTabIcon(0, QIcon("resources/svg/tab_verse.svg"))
        self.tabs.setTabIcon(1, QIcon("resources/svg/tab_search.svg"))
        self.tabs.setTabIcon(2, QIcon("resources/svg/tab_font.svg"))

    def update_poll_button_text(self):
        """
        Updates the polling toggle button text based on polling state.
        """
        if self.poll_toggle_btn.isChecked():
            self.poll_toggle_btn.setText(self.tr("toggle_btn_poll_enabled"))
            self.poll_toggle_btn.setIcon(QIcon("resources/svg/toggle_btn_poll_enabled.svg"))
        else:
            self.poll_toggle_btn.setText(self.tr("toggle_btn_poll_disabled"))
            self.poll_toggle_btn.setIcon(QIcon("resources/svg/toggle_btn_poll_disabled.svg"))
        self.poll_toggle_btn.setIconSize(QSize(30, 30))

    def on_poll_toggle_clicked(self):
        """
        Handles the polling toggle button click event.

        - Saves polling state to config.
        - Updates tab_settings.
        - Applies/restarts polling.
        - Updates toggle button text and version tab button layout.
        """
        poll_enabled = self.poll_toggle_btn.isChecked()
        ConfigManager.update_partial({"poll_enabled": poll_enabled})
        self.tab_settings.settings["poll_enabled"] = poll_enabled
        self.tab_settings.apply_polling_settings()
        self.update_poll_button_text()
        self.tab_verse.update_button_layout()
        self.tab_keyword.update_button_visibility()

    def show_about(self):
        """
        Displays the About dialog.
        """
        QMessageBox.about(
            self,
            self.tr("about_title"),
            self.tr("about_message").format(self.app_version)
        )

    def open_monitor_memory(self):
        """
        Opens the real-time memory monitor window.
        """
        settings = ConfigManager.load()
        interval = settings.get("memory_interval_sec", 5)
        self.monitor_window = MonitorMemory(interval_sec=interval)
        self.monitor_window.show()

    def trigger_error(self):
        """
        Deliberately triggers a ZeroDivisionError for testing error handling.
        Used to validate logging and critical error dialogs.
        """
        try:
            x = 1 / 0
        except Exception as e:
            from gui.utils.logger import handle_exception
            handle_exception(e, "Error Test", "This is a drill.")

    def closeEvent(self, event):
        """
        Handles cleanup and settings saving before application closes.

        Args:
            event (QCloseEvent): The close event.
        """
        try:
            tab_verse = self.tabs.widget(0)

            font_tab = self.tabs.widget(2)
            from gui.ui.tab_settings import TabSettings
            if isinstance(font_tab, TabSettings):
                font_tab.apply_dynamic_settings()

            from gui.utils.state_saver import save_settings_from_ui
            save_settings_from_ui(QApplication.instance(), tab_verse)

            tab_settings = self.tabs.widget(3)
            from gui.ui.tab_settings import TabSettings
            if isinstance(tab_settings, TabSettings) and tab_settings.overlay:
                tab_settings.overlay.close()

        except Exception as e:
            QMessageBox.critical(self, 
                self.tr("error_set_saving_title"), 
                self.tr("error_set_saving_msg").format(e))
        event.accept()