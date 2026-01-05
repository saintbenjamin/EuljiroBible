# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/ui/tab_settings.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Implements the :class:`gui.ui.tab_settings.TabSettings` class for managing application fonts, overlay behavior, polling, and output path configuration.
"""

from PySide6.QtCore import QTimer, QCoreApplication
from PySide6.QtWidgets import QWidget, QMessageBox, QApplication

from core.utils.file_helpers import should_show_overlay
from core.utils.logger import log_debug
from gui.config.config_manager import ConfigManager
from gui.ui.locale.message_loader import load_messages
from gui.ui.tab_settings_ui import TabSettingsUI
from gui.ui.tab_settings_logic import TabSettingsLogic
from gui.utils.overlay_factory import create_overlay
from gui.utils.utils_display import get_display_descriptions
from gui.utils.utils_theme import set_dark_mode

class TabSettings(QWidget, TabSettingsUI):
    """
    Settings tab widget for configuring application behavior and overlay display.

    This tab provides UI and orchestration for user-adjustable settings such as
    fonts, theme mode, overlay display configuration, output file path selection,
    and the polling mechanism that monitors the verse output file.

    Most per-feature operations are delegated to TabSettingsLogic, while this class
    coordinates the Qt timer, overlay window lifecycle, and language refresh.

    Attributes:
        tr (Callable[[str], str]): Translation function for UI labels and messages.
        app (QApplication): Qt application instance used for theme changes and global styling.
        settings (dict): Shared application settings dictionary (loaded and persisted via ConfigManager).
        verse_path (str): Path to the verse output file used by polling/overlay logic.
        poll_timer (QTimer): Timer that periodically triggers polling of the verse output file.
        refresh_settings_callback (Callable[[], None]): Callback invoked when settings should be refreshed
            outside of this tab.
        get_poll_enabled (Callable[[], bool]): Callback returning whether polling is enabled externally.
        overlay (QWidget | None): Active overlay window instance when enabled; otherwise None.
        overlay_denied (bool): Flag indicating the user denied overlay usage on single-display setups.
        logic (TabSettingsLogic): Backend logic handler for applying UI-driven settings changes.

    Note:
        The following callable is intentionally omitted from ``Attributes`` to avoid duplicate autodoc entries, as it is already documented as a class method:

        - get_main_geometry (Callable[[], QRect]): Callback returning the main window geometry used to determine which screen is treated as the "main" display.
    """

    def __init__(self, app, settings, tr, get_poll_enabled_callback=None, get_main_geometry=None, refresh_settings_callback=None):
        """
        Initialize the settings tab with application context and user settings.

        This sets up the polling timer, installs optional callbacks, initializes the
        logic backend, and builds the UI.

        Args:
            app (QApplication): QApplication instance.
            settings (dict): Shared settings dictionary.
            tr (Callable[[str], str]): Translation function for UI labels.
            get_poll_enabled_callback (Callable[[], bool] | None): Optional callback that returns
                whether polling is enabled externally.
            get_main_geometry (Callable[[], QRect] | None): Optional callback that returns the main
                window geometry used for screen selection logic.
            refresh_settings_callback (Callable[[], None] | None): Optional callback invoked when
                settings should be refreshed outside this tab.
        """
        super().__init__()
        self.tr = tr
        self.app = app
        self.settings = settings
        self.verse_path = self.settings.get("output_path", "verse_output.txt")

        # Timer for polling verse output file
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll_file)
        if self.settings.get("poll_enabled", False):
            self.poll_timer.start(self.settings.get("poll_interval", 1000))

        self.get_main_geometry = get_main_geometry or self.get_main_geometry
        self.refresh_settings_callback = refresh_settings_callback or (lambda: None)

        self.overlay = None
        self.get_poll_enabled = get_poll_enabled_callback or (lambda: False)
        self.logic = TabSettingsLogic(app, settings, tr, refresh_settings_callback)

        self.init_ui()

    def change_language(self, lang_code):
        """
        Update all labels and buttons to reflect a new language setting.

        This updates visible UI text, persists the selected language in settings,
        and writes the change through ConfigManager.

        Args:
            lang_code (str): Language code (e.g., "ko", "en").
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
        self.always_on_off_checkbox.setText(self.tr("checkbox_show_on_off"))
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
        """
        Apply all dynamic settings through the logic module.

        This delegates to TabSettingsLogic to apply the current UI selections to the
        application and persisted settings.
        """
        self.logic.apply_dynamic_settings(self)

    def apply_font_to_children(self, widget, font):
        """
        Apply a font to child widgets recursively.

        Args:
            widget (QWidget): Root widget whose children should receive the font.
            font (QFont): Font to apply.
        """
        self.logic.apply_font_to_children(self)

    def select_text_color(self):
        """
        Open a color picker dialog to select the display text color.

        This delegates to TabSettingsLogic, which updates both UI previews and persisted settings.
        """
        self.logic.select_text_color(self)

    def select_bg_color(self):
        """
        Open a color picker dialog to select the display background color.

        This delegates to TabSettingsLogic, which updates both UI previews and persisted settings.
        """
        self.logic.select_bg_color(self)

    def select_output_path(self):
        """
        Open a file browser dialog to select the verse output path.

        This delegates to TabSettingsLogic, which validates and stores the selected path.
        """
        self.logic.select_output_path(self)

    def apply_polling_settings(self):
        """
        Apply polling settings and restart polling if enabled.

        This delegates to TabSettingsLogic to validate the polling interval, update settings,
        and start/stop the polling timer as needed.
        """
        self.logic.apply_polling_settings(self)

    def save_poll_interval(self, parent):
        """
        Save the polling interval value from the UI.

        This delegates to TabSettingsLogic, which validates the input and persists it.
        """
        self.logic.save_poll_interval(self)

    def toggle_theme(self):
        """
        Toggle between dark and light application themes.

        This flips the current theme state, applies the stylesheet accordingly, updates
        the settings dictionary, and persists the change via :class:`gui.config.config_manager.ConfigManager`.
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
        Toggle the overlay display on or off.

        When enabling, this determines the target screen geometry based on the current
        overlay mode (fullscreen vs resizable), screen count, and the main window
        geometry. When disabling, it closes the active overlay window.

        This method also respects a user-denial flag for single-display setups.

        Note:
            - In fullscreen mode, the overlay prefers a secondary monitor if available.
            - In resizable mode, the overlay uses the user-selected display index.
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
            main_geom = self.get_main_geometry()
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

    def get_main_geometry(self):
        """
        Return the main window geometry.

        This is a stub fallback used when no external callback is injected. Call sites
        should inject a real geometry provider so overlay placement logic can determine
        the primary screen reliably.

        Returns:
            QRect: Geometry of the main window (fallback is a zero rect).
        """
        print("get_main_geometry internally called")
        from PySide6.QtCore import QRect
        return QRect(0, 0, 0, 0)

    def populate_displays(self):
        """
        Populate the display dropdown with available screen descriptions.

        This clears the display combo box and fills it with human-readable display names.
        """
        self.display_combo.clear()
        self.display_combo.addItems(get_display_descriptions())

    def ensure_overlay_on(self):
        """
        Ensure the overlay window is visible, enabling it if necessary.

        If overlay usage was previously denied by the user, this does nothing.
        """
        if getattr(self, "overlay_denied", False):
            log_debug("[TabSettings] ensure_overlay_on skipped: previously denied")
            return

        if not self.overlay or not self.overlay.isVisible():
            self.toggle_overlay()

    def poll_file(self):
        """
        Poll the verse output file and control overlay visibility.

        If polling is disabled, any active overlay is closed. If polling is enabled,
        the overlay is shown when the verse output file indicates content should be
        displayed, and hidden when the output is empty.

        This method is intended to be called periodically by poll_timer.
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
        Update visibility of the overlay configuration group.

        Visibility is determined by the effective polling state, defined as:
        polling enabled OR the "always show on/off buttons" setting enabled.
        """
        self.settings["always_show_on_off_buttons"] = self.always_on_off_checkbox.isChecked()

        always_on = self.settings.get("always_show_on_off_buttons", False)
        poll_enabled = self.get_poll_enabled()
        effective_polling = poll_enabled or always_on

        if effective_polling:
            self.overlay_group.show()
        else:
            self.overlay_group.hide()