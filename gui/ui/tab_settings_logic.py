# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/ui/tab_settings_logic.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Handles backend logic for the settings tab: dynamic UI updates, file paths, colors, and polling behavior.
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
    Backend logic handler for the settings tab.

    This class encapsulates non-UI operations used by TabSettings, including:
    font application, overlay configuration persistence, polling interval validation,
    output path selection, and color picker actions.

    Attributes:
        settings (dict): Shared application settings dictionary.
        app (QApplication): Qt application instance used for theme/style updates.
        tr (Callable[[str], str]): Translation function for localized UI strings.
        refresh_settings_callback (Callable[[], None] | None): Optional callback to refresh
            other UI tabs/components after settings changes.
    """

    def __init__(self, settings, app, tr_func, refresh_settings_callback):
        """
        Initialize the settings logic handler.

        Args:
            settings (dict): Shared application settings dictionary.
            app (QApplication): QApplication instance.
            tr_func (Callable[[str], str]): Translation function for localized messages.
            refresh_settings_callback (Callable[[], None] | None): Optional callback invoked
                after applying settings to refresh other UI components.
        """
        self.settings = settings
        self.app = app
        self.tr = tr_func
        self.refresh_settings_callback = refresh_settings_callback

    def apply_dynamic_settings(self, parent):
        """
        Apply dynamic font and overlay display settings.

        This applies the main application font, collects overlay display settings from
        the UI widgets, persists them via ConfigManager, and updates the active overlay
        window if it is currently shown. If a refresh callback is provided, it is called
        to propagate the updated settings to other tabs.

        Args:
            parent (QWidget): TabSettings instance providing current UI widget state.
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
        Apply a font to a widget and all of its child widgets.

        Args:
            parent (QWidget): Root window or settings tab context (kept for signature consistency).
            widget (QWidget): Target widget to apply the font to.
            font (QFont): Font to apply.
        """
        widget.setFont(font)
        for child in widget.findChildren(QWidget):
            child.setFont(font)

    def select_output_path(self, parent):
        """
        Open a file dialog to select the verse output file path.

        If the user selects a path, this updates the UI field and persists the value
        to settings via ConfigManager.

        Args:
            parent (QWidget): TabSettings instance containing the path UI field and settings.
        """
        current_path = parent.output_edit.text()
        path = get_save_path(parent, current_path, parent.tr("dialog_path"))
        if path:
            parent.output_edit.setText(path)
            parent.settings["output_path"] = path
            ConfigManager.update_partial({"output_path": path})

    def select_text_color(self, parent):
        """
        Open a color picker dialog to set the overlay text color.

        This updates the color preview, persists the setting, and triggers reapplication
        of dynamic settings.

        Args:
            parent (QWidget): TabSettings instance containing the text color UI button.
        """
        set_color_from_dialog(parent.text_color_btn, "display_text_color", parent.apply_dynamic_settings)

    def select_bg_color(self, parent):
        """
        Open a color picker dialog to set the overlay background color.

        This updates the color preview, persists the setting, and triggers reapplication
        of dynamic settings.

        Args:
            parent (QWidget): TabSettings instance containing the background color UI button.
        """
        set_color_from_dialog(parent.bg_color_btn, "display_bg_color", parent.apply_dynamic_settings)

    def save_poll_interval(self, parent):
        """
        Validate and save the polling interval from the UI.

        If the interval is not a valid integer, this shows a warning dialog and does not
        persist any changes. On success, the interval is saved to settings via ConfigManager.

        Args:
            parent (QWidget): TabSettings instance containing the polling interval input widget.
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
        Apply polling timer behavior based on the current settings.

        If polling is enabled, this restarts the polling timer using the configured
        interval and performs an immediate poll. If polling is disabled, this stops
        the timer and closes any active overlay window.

        Args:
            parent (QWidget): TabSettings instance owning the polling timer and overlay window.
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