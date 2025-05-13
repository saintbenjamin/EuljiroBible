# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_settings_logic.py
Handles backend logic for the settings tab: dynamic UI updates, file paths, colors, and polling behavior.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtWidgets import QWidget, QMessageBox

from core.utils.input_validators import validate_int
from core.utils.logger import log_debug

from gui.config.config_manager import ConfigManager
from gui.constants import messages

from gui.utils.settings_helper import update_overlay_settings
from gui.utils.utils_fonts import apply_main_font_to_app, apply_overlay_font
from gui.utils.utils_dialog import get_save_path, set_color_from_dialog

class TabSettingsLogic:
    """
    Provides logic operations for the settings tab UI.

    Handles font application, theme updates, polling intervals, path selections, and color pickers.

    :param settings: Shared application settings dictionary
    :type settings: dict
    :param app: QApplication instance
    :type app: QApplication
    :param tr_func: Translation function for localized messages
    :type tr_func: Callable[[str], str]
    """

    def __init__(self, settings, app, tr_func, refresh_settings_callback):
        """
        Initialize settings logic handler.

        :param settings: Settings dictionary
        :param app: QApplication instance
        :param tr_func: Translation function
        """
        self.settings = settings
        self.app = app
        self.tr = tr_func
        self.refresh_settings_callback = refresh_settings_callback

    def apply_dynamic_settings(self, parent):
        """
        Apply font, overlay, and display settings to the application.

        :param parent: Reference to the TabSettings instance (contains UI state)
        :type parent: QWidget
        """
        if not hasattr(parent, "display_font_size_combo"):
            return

        # Apply font to all widgets in the app
        apply_main_font_to_app(
            parent.font_family_combo.currentText(),
            int(parent.font_size_combo.currentText()),
            parent.font_weight_combo.currentData(),
            parent.window()
        )

        # Collect current overlay settings from UI and update
        updated_overlay = update_overlay_settings(parent.settings, {
            "font_family_combo": parent.display_font_family_combo,
            "font_size_combo": parent.display_font_size_combo,
            "font_weight_combo": parent.display_font_weight_combo,
            "alpha_slider": parent.alpha_slider,
            "text_color_btn": parent.text_color_btn,
            "bg_color_btn": parent.bg_color_btn,
            "mode_combo": parent.overlay_mode_combo
        })
        ConfigManager.update_partial(updated_overlay)

        # Save on/off visibility setting
        always_show_on_off = parent.always_on_off_checkbox.isChecked()
        ConfigManager.update_partial({"always_show_on_off_buttons": always_show_on_off})
        parent.settings["always_show_on_off_buttons"] = always_show_on_off

        # Apply overlay font if overlay is active
        if parent.overlay:
            apply_overlay_font(parent.overlay, parent.settings)

        # Reload all tabs with new settings
        if self.refresh_settings_callback:
            self.refresh_settings_callback()

    def apply_font_to_children(self, parent, widget, font):
        """
        Recursively apply a font to a widget and its children.

        :param parent: Root window
        :type parent: QWidget
        :param widget: Target widget to apply font to
        :type widget: QWidget
        :param font: QFont instance
        :type font: QFont
        """
        widget.setFont(font)
        for child in widget.findChildren(QWidget):
            child.setFont(font)

    def select_output_path(self, parent):
        """
        Open a file dialog to set the verse output file path.

        :param parent: TabSettings instance with path input field
        :type parent: QWidget
        """
        current_path = parent.output_edit.text()
        path = get_save_path(parent, current_path, parent.tr("dialog_path"))
        if path:
            parent.output_edit.setText(path)
            parent.settings["output_path"] = path
            ConfigManager.update_partial({"output_path": path})

    def select_text_color(self, parent):
        """
        Open a color picker dialog to select the overlay text color.

        Updates button color, saves to settings, and reapplies dynamic settings.

        :param parent: TabSettings instance
        :type parent: QWidget
        """
        set_color_from_dialog(parent.text_color_btn, "display_text_color", parent.apply_dynamic_settings)

    def select_bg_color(self, parent):
        """
        Open a color picker dialog to select the overlay background color.

        Updates button color, saves to settings, and reapplies dynamic settings.

        :param parent: TabSettings instance
        :type parent: QWidget
        """
        set_color_from_dialog(parent.bg_color_btn, "display_bg_color", parent.apply_dynamic_settings)

    def save_poll_interval(self, parent):
        """
        Save the polling interval from the input box.

        If the value is not a valid integer, show a warning dialog.

        :param parent: TabSettings instance
        :type parent: QWidget
        """
        text = parent.poll_input.text()

        # Check validity of interval value
        valid, interval = validate_int(text)
        if not valid:
            QMessageBox.warning(
                parent,
                messages.ERROR_MESSAGES["POLL_INTERVAL_INVALID_TITLE"],
                messages.ERROR_MESSAGES["POLL_INTERVAL_INVALID_MSG"]
            )
            return

        # Save the valid interval to disk and memory
        parent.settings["poll_interval"] = interval
        ConfigManager.save(self.settings)
        log_debug(f"Saved poll interval: {interval}")

    def apply_polling_settings(self, parent):
        """
        Apply polling logic: start or stop polling based on toggle.

        :param parent: TabSettings instance
        :type parent: QWidget
        """
        poll_enabled = parent.settings.get("poll_enabled", False)
        poll_interval = parent.settings.get("poll_interval", 1000)

        if poll_enabled:
            if parent.poll_timer.isActive():
                parent.poll_timer.stop()
            parent.poll_timer.start(poll_interval)
            log_debug("[TabSettings] polling restarted")
            parent.poll_file()
        else:
            if parent.poll_timer.isActive():
                parent.poll_timer.stop()
            log_debug("[TabSettings] polling stopped")

            # If overlay is active, close it when polling is turned off
            if parent.overlay and parent.overlay.isVisible():
                parent.overlay.close()
                parent.overlay = None
                log_debug("[TabSettings] overlay turned OFF due to polling OFF")