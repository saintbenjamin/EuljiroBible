# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_settings.py
Implements the TabSettings class for managing application fonts, overlay behavior, polling, and output path configuration.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtCore import QTimer, QCoreApplication
from PySide6.QtWidgets import QWidget, QMessageBox, QApplication

from core.utils.file_helpers import should_show_overlay
from core.utils.logger import log_debug
from gui.config.config_manager import ConfigManager
from gui.ui.locale.message_loader import load_messages
from gui.utils.overlay_factory import create_overlay
from gui.utils.utils_display import get_display_descriptions
from gui.utils.utils_theme import set_dark_mode
from gui.utils.utils_window import find_window_main

from gui.ui.tab_settings_ui import TabSettingsUI
from gui.ui.tab_settings_logic import TabSettingsLogic


class TabSettings(QWidget, TabSettingsUI):
    """
    Provides the UI and logic for application settings including fonts, themes,
    overlay display configuration, file output path, and polling mechanism.
    """

    def __init__(self, app, settings, overlay_callback, tr, get_poll_enabled_callback=None):
        """
        Initializes the settings tab with provided context.

        :param app: QApplication instance
        :type app: QApplication
        :param settings: Shared settings dictionary
        :type settings: dict
        :param overlay_callback: Callback function to control overlay
        :type overlay_callback: Callable
        :param tr: Translation function
        :type tr: Callable[[str], str]
        :param get_poll_enabled_callback: Optional polling state checker
        :type get_poll_enabled_callback: Callable or None
        """
        super().__init__()
        self.tr = tr
        self.app = app
        self.settings = settings
        self.verse_path = self.settings.get("output_path", "verse_output.txt")
        self.overlay_callback = overlay_callback

        # Timer for polling verse output file
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll_file)
        if self.settings.get("poll_enabled", False):
            self.poll_timer.start(self.settings.get("poll_interval", 1000))

        self.overlay = None
        self.get_poll_enabled = get_poll_enabled_callback or (lambda: False)
        self.logic = TabSettingsLogic(app, settings, tr)

        self.init_ui()

    def change_language(self, lang_code):
        """
        Updates all labels and buttons to reflect a new language setting.

        :param lang_code: Language code (e.g. 'ko', 'en')
        :type lang_code: str
        """
        self.current_language = lang_code
        self.messages = load_messages(lang_code)

        # Main settings section
        self.font_family_label.setText(self.tr("label_font_family"))
        self.font_size_label.setText(self.tr("label_font_size"))
        self.font_weight_label.setText(self.tr("label_font_weight"))
        self.theme_toggle_btn.setText(self.tr("btn_theme_toggle"))
        self.main_group.setTitle(self.tr("setting_main"))

        # Overlay and polling section
        self.overlay_group.setTitle(self.tr("setting_overlay"))
        self.poll_label.setText(self.tr("label_poll_interval"))
        self.poll_save.setText(self.tr("btn_poll_interval_save"))
        self.always_on_off_checkbox.setText(self.tr("checkbox_show_on_off_buttons"))
        self.overlay_mode_combo.setItemText(0, self.tr("fullscreen"))
        self.overlay_mode_combo.setItemText(1, self.tr("resizable"))
        self.display_font_family_label.setText(self.tr("label_font_family"))
        self.display_font_size_label.setText(self.tr("label_font_size"))
        self.display_font_weight_label.setText(self.tr("label_font_weight"))
        self.display_font_color_label.setText(self.tr("label_display_font_color"))
        self.bg_color_label.setText(self.tr("label_display_bg_color"))
        self.bg_alpha_label.setText(self.tr("label_display_bg_alpha"))
        self.path_label.setText(self.tr("label_path"))
        self.browse_btn.setText(self.tr("btn_browse"))

        # Save selected language
        self.settings["last_language"] = lang_code
        ConfigManager.update_partial({"last_language": lang_code})

    def apply_dynamic_settings(self):
        """Applies all dynamic settings through logic module."""
        self.logic.apply_dynamic_settings(self)

    def apply_font_to_children(self, widget, font):
        """Applies font to all child widgets recursively."""
        self.logic.apply_font_to_children(self)

    def select_text_color(self):
        """Opens color dialog to select text color."""
        self.logic.select_text_color(self)

    def select_bg_color(self):
        """Opens color dialog to select background color."""
        self.logic.select_bg_color(self)

    def select_output_path(self):
        """Opens file browser to select output path."""
        self.logic.select_output_path(self)

    def apply_polling_settings(self):
        """Applies polling settings and restarts polling if enabled."""
        self.logic.apply_polling_settings(self)

    def save_poll_interval(self, parent):
        """Saves polling interval value from UI."""
        self.logic.save_poll_interval(self)

    def toggle_theme(self):
        """
        Toggles between dark and light application themes.
        """
        log_debug("[TabSettings] toggle_theme called")
        enable = not bool(self.app.styleSheet())
        set_dark_mode(self.app, enable)
        self.settings["dark_mode"] = enable
        log_debug(f"[TabSettings] dark mode {'ON' if enable else 'OFF'}")

        try:
            ConfigManager.update_partial({"dark_mode": enable})
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("error_set_saving_title"),
                self.tr("error_set_saving_msg").format(e)
            )

    def toggle_overlay(self):
        """
        Turns the overlay display on or off based on its current state.
        Uses screen geometry logic to determine placement.
        """
        log_debug("[TabSettings] toggle_overlay called")

        if getattr(self, "overlay_denied", False):
            log_debug("[TabSettings] overlay was previously denied by user")
            return

        self.settings = ConfigManager.load()

        if self.overlay and self.overlay.isVisible():
            self.overlay.close()
            self.overlay = None
            log_debug("[TabSettings] overlay turned OFF")
            return

        screens = QApplication.screens()
        screen_count = len(screens)
        is_fullscreen = self.settings.get("display_overlay_mode", "fullscreen") == "fullscreen"

        if is_fullscreen:
            main_window = find_window_main(self)
            main_geom = main_window.frameGeometry()
            main_screen = QApplication.screenAt(main_geom.center())

            if screen_count > 1:
                other_screens = [s for s in screens if s != main_screen]
                target_geometry = other_screens[0].geometry()
            else:
                if not QCoreApplication.instance().property("warned_display_once"):
                    reply = QMessageBox.question(
                        self,
                        self.tr("warning_single_display_title"),
                        self.tr("warning_single_display_msg"),
                        QMessageBox.Yes | QMessageBox.No
                    )
                    QCoreApplication.instance().setProperty("warned_display_once", True)
                    if reply != QMessageBox.Yes:
                        self.overlay_denied = True
                        return
                target_geometry = screens[0].geometry()
        else:
            index = self.display_combo.currentIndex()
            target_geometry = (
                screens[index].geometry()
                if 0 <= index < screen_count else
                QApplication.primaryScreen().geometry()
            )

        self.overlay = create_overlay(self.settings, target_geometry, parent=self)
        self.overlay.show()
        log_debug("[TabSettings] overlay turned ON")

    def populate_displays(self):
        """
        Fills the display dropdown with screen descriptions.
        """
        self.display_combo.clear()
        self.display_combo.addItems(get_display_descriptions())

    def ensure_overlay_on(self):
        """
        Ensures the overlay is visible, enabling it if necessary.
        """
        if getattr(self, "overlay_denied", False):
            log_debug("[TabSettings] ensure_overlay_on skipped: previously denied")
            return

        if not self.overlay or not self.overlay.isVisible():
            self.toggle_overlay()

    def poll_file(self):
        """
        Periodically checks the verse output file and controls overlay visibility.
        """
        if not self.settings.get("poll_enabled", False):
            if self.overlay and self.overlay.isVisible():
                self.overlay.close()
                self.overlay = None
                log_debug("[TabSettings] overlay turned OFF due to polling OFF")
            return

        if should_show_overlay(self.verse_path):
            if not self.overlay or not self.overlay.isVisible():
                self.ensure_overlay_on()
        else:
            if self.overlay and self.overlay.isVisible():
                self.overlay.close()
                self.overlay = None
                log_debug("[TabSettings] overlay turned OFF due to empty verse")

    def update_presentation_visibility(self):
        """
        Shows or hides the overlay configuration group based on polling or always-show setting.
        """
        always_on = self.settings.get("always_show_on_off_buttons", False)
        poll_enabled = self.get_poll_enabled()
        effective_polling = poll_enabled or always_on

        if effective_polling:
            self.overlay_group.show()
        else:
            self.overlay_group.hide()