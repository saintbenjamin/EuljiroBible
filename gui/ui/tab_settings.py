# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/ui/tab_settings.py
Implements the TabSettings for EuljiroBible, managing font settings, overlay display settings, file output paths, and polling.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

# PySide6 modules
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QMessageBox, QApplication 
from PySide6.QtCore import QCoreApplication

# Core utilities
from core.utils.file_helpers import should_show_overlay
from core.utils.logger import log_debug

# GUI config and constants
from gui.config.config_manager import ConfigManager

# Localization
from gui.ui.locale.message_loader import load_messages

# Overlay logic
from gui.utils.overlay_factory import create_overlay

# Display/font/theme/window helpers
from gui.utils.utils_display import get_display_descriptions
from gui.utils.utils_theme import set_dark_mode
from gui.utils.utils_window import find_window_main

from gui.ui.tab_settings_ui import TabSettingsUI
from gui.ui.tab_settings_logic import TabSettingsLogic

class TabSettings(QWidget, TabSettingsUI):
    """
    Tab for configuring application fonts, overlay display settings, output paths, and polling behavior.

    Attributes:
        app (QApplication): Main application instance.
        settings (dict): Loaded user settings.
        overlay_callback (callable): Callback for toggling overlay.
        verse_path (str): Path to the verse output file.
        poll_timer (QTimer): Timer for polling the output file.
        overlay (WidgetOverlay): Overlay widget instance if active.
    """
    def __init__(self, app, settings, overlay_callback, tr, get_poll_enabled_callback=None):
        """
        Initializes the TabSettings.

        Args:
            app (QApplication): Main application instance.
            settings (dict): Loaded user settings.
            overlay_callback (function): Callback to control overlay display.
            tr (function): Translation function for UI text.
            get_poll_enabled_callback (function, optional): Function to check if polling is enabled.
        """
        super().__init__()
        self.tr = tr
        self.app = app
        self.settings = settings
        self.verse_path = self.settings.get("output_path", "verse_output.txt")
        self.overlay_callback = overlay_callback

        # Setup polling timer
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
        Changes the language of all labels and buttons dynamically.

        Args:
            lang_code (str): Language code.
        """
        self.current_language = lang_code
        self.messages = load_messages(lang_code)

        # Update main panel texts
        self.font_family_label.setText(self.tr("label_font_family"))
        self.font_size_label.setText(self.tr("label_font_size"))
        self.font_weight_label.setText(self.tr("label_font_weight"))
        self.theme_toggle_btn.setText(self.tr("btn_theme_toggle"))
        self.main_group.setTitle(self.tr("setting_main"))
        self.overlay_group.setTitle(self.tr("setting_overlay"))

        # Update polling texts
        self.poll_label.setText(self.tr("label_poll_interval"))
        self.poll_save.setText(self.tr("btn_poll_interval_save"))
        self.always_on_off_checkbox.setText(self.tr("checkbox_show_on_off"))

        # Update overlay font/display section
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

        # Persist language choice
        self.settings["last_language"] = lang_code
        ConfigManager.update_partial({"last_language": lang_code})

    def apply_dynamic_settings(self):
        self.logic.apply_dynamic_settings(self)

    def apply_font_to_children(self, widget, font):
        self.logic.apply_font_to_children(self)

    def select_text_color(self):
        self.logic.select_text_color(self)

    def select_bg_color(self):
        self.logic.select_bg_color(self)

    def select_output_path(self):
        self.logic.select_output_path(self)

    def apply_polling_settings(self):
        self.logic.apply_polling_settings(self)

    def save_poll_interval(self, parent):
        self.logic.save_poll_interval(self)

    def toggle_theme(self):
        """
        Toggles between dark mode and light mode for the application.
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
                self.tr("error_set_saving_msg").format(e),
            )

    def toggle_overlay(self):
        """
        Turns the overlay on or off based on current state, with smart display selection in worship mode.
        """
        log_debug("[TabSettings] toggle_overlay called")

        # Prevents reopening if user has previously denied overlay on single screen
        if getattr(self, "overlay_denied", False):
            log_debug("[TabSettings] overlay was previously denied by user")
            return

        # Reload settings to reflect recent changes
        self.settings = ConfigManager.load()

        # If overlay is already visible, close it
        if self.overlay and self.overlay.isVisible():
            self.overlay.close()
            self.overlay = None
            log_debug("[TabSettings] overlay turned OFF")
            return

        screens = QApplication.screens()
        screen_count = len(screens)

        # Determine overlay mode
        is_fullscreen = self.settings.get("display_overlay_mode", "fullscreen") == "fullscreen"

        if is_fullscreen:
            # Get main screen geometry
            main_window = find_window_main(self)
            main_geom = main_window.frameGeometry()
            main_screen = QApplication.screenAt(main_geom.center())

            if screen_count > 1:
                # Use the other screen for overlay if available
                other_screens = [s for s in screens if s != main_screen]
                target_geometry = other_screens[0].geometry()
            else:
                # Ask user for confirmation on single-display setup, but only once
                log_debug("[TabSettings] about to ask single-display warning")
                app = QCoreApplication.instance()
                if not app.property("warned_display_once"):
                    reply = QMessageBox.question(
                        self,
                        self.tr("warning_single_display_title"),
                        self.tr("warning_single_display_msg"),
                        QMessageBox.Yes | QMessageBox.No
                    )
                    app.setProperty("warned_display_once", True)

                    if reply != QMessageBox.Yes:
                        log_debug("[TabSettings] User cancelled overlay due to single screen.")
                        self.overlay_denied = True
                        return

                target_geometry = screens[0].geometry()
        else:
            # Resizable overlay: use selected screen index or fallback to primary screen
            index = self.display_combo.currentIndex()
            target_geometry = (
                screens[index].geometry()
                if 0 <= index < screen_count
                else QApplication.primaryScreen().geometry()
            )

        # Create and show overlay window
        self.overlay = create_overlay(self.settings, target_geometry, parent=self)
        self.overlay.show()
        log_debug("[TabSettings] overlay turned ON")

    def populate_displays(self):
        """
        Populates the display dropdown with available screens.
        """
        self.display_combo.clear()
        self.display_combo.addItems(get_display_descriptions())

    def ensure_overlay_on(self):
        """
        Ensures the overlay is active; turns it on if necessary.
        """
        if getattr(self, "overlay_denied", False):
            log_debug("[TabSettings] ensure_overlay_on skipped: overlay was previously denied by user")
            return

        if not self.overlay or not self.overlay.isVisible():
            self.toggle_overlay()

    def poll_file(self):
        """
        Polls the output file and updates overlay visibility based on file content.
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
        Shows or hides presentation settings based on toggle and polling settings.
        """
        always_on = self.settings.get("always_show_on_off_buttons", False)
        poll_enabled = self.get_poll_enabled()
        effective_polling = poll_enabled or always_on

        if effective_polling:
            self.overlay_group.show()
        else:
            self.overlay_group.hide()