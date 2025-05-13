# tab_settings_logic.py

# PySide6 modules
from PySide6.QtWidgets import QWidget, QMessageBox

# Core utilities
from core.utils.input_validators import validate_int
from core.utils.logger import log_debug

# GUI config and constants
from gui.config.config_manager import ConfigManager
from gui.constants import messages

# Overlay logic
from gui.utils.settings_helper import update_overlay_settings

# Display/font/theme/window helpers
from gui.utils.utils_fonts import apply_main_font_to_app, apply_overlay_font
from gui.utils.utils_theme import refresh_main_tabs
from gui.utils.utils_window import find_window_main

# Dialog utilities
from gui.utils.utils_dialog import get_save_path, set_color_from_dialog

class TabSettingsLogic:
    """
    Handles core logic for settings tab: font, polling, path, color selection.
    """

    def __init__(self, settings, app, tr_func):
        """
        Args:
            settings (dict): Shared settings dictionary
            app (QApplication): Application instance
            tr_func (callable): Translation function
        """
        self.settings = settings
        self.app = app
        self.tr = tr_func


    def apply_dynamic_settings(self, parent):
        """
        Applies font, overlay, style settings, and updates button visibility dynamically.

        Args:
            parent: The TabSettings instance containing the UI widgets.
        """
        if not hasattr(parent, "display_font_size_combo"):
            return

        # ✅ Apply main font to the entire application
        apply_main_font_to_app(
            parent.font_family_combo.currentText(),
            int(parent.font_size_combo.currentText()),
            parent.font_weight_combo.currentData(),
            parent.window()
        )

        # ✅ Update overlay settings from current widgets
        updated_overlay = update_overlay_settings(parent.settings, {
            "font_family_combo": parent.display_font_family_combo,
            "font_size_combo": parent.display_font_size_combo,
            "font_weight_combo": parent.display_font_weight_combo,
            "alpha_slider": parent.alpha_slider,
            "text_color_btn": parent.text_color_btn,
            "bg_color_btn": parent.bg_color_btn,
            "mode_combo": parent.overlay_mode_combo
        })

        # ✅ Save overlay settings
        ConfigManager.update_partial(updated_overlay)

        # ✅ Save ON/OFF visibility toggle
        always_show_on_off = parent.always_on_off_checkbox.isChecked()
        ConfigManager.update_partial({"always_show_on_off_buttons": always_show_on_off})
        parent.settings["always_show_on_off_buttons"] = always_show_on_off

        # ✅ Reapply font to overlay
        if parent.overlay:
            apply_overlay_font(parent.overlay, parent.settings)

        # ✅ Refresh settings and reload all tabs
        window_main = find_window_main(parent)
        if window_main:
            window_main.settings = ConfigManager.load()
            refresh_main_tabs(window_main)

    def apply_font_to_children(self, parent, widget, font):
        """
        Recursively applies the font to all child widgets.

        Args:
            widget (QWidget): Parent widget.
            font (QFont): Font to apply.
        """
        widget.setFont(font)
        for child in widget.findChildren(QWidget):
            child.setFont(font)

    def select_output_path(self, parent):
        """
        Opens a file dialog to select output path for verse output.
        """
        current_path = parent.output_edit.text()
        path = get_save_path(parent, current_path, parent.tr("dialog_path"))
        if path:
            parent.output_edit.setText(path)
            parent.settings["output_path"] = path
            ConfigManager.update_partial({"output_path": path})

    def select_text_color(self, parent):
        """
        Opens a color dialog to select the overlay text color.

        On valid color selection, updates the button style,
        saves the selected color to settings, and reapplies dynamic settings.
        """
        set_color_from_dialog(parent.text_color_btn, "display_text_color", parent.apply_dynamic_settings)

    def select_bg_color(self, parent):
        """
        Opens a color dialog to select the overlay background color.

        On valid color selection, updates the button style,
        saves the selected color to settings, and reapplies dynamic settings.
        """
        set_color_from_dialog(parent.bg_color_btn, "display_bg_color", parent.apply_dynamic_settings)

    def save_poll_interval(self, parent):
        """
        Saves the polling interval for overlay updates.

        Validates that the entered value is an integer.
        On success, updates the settings and saves them to disk.
        If invalid, shows a warning message box to the user.
        """
        text = parent.poll_input.text()

        # Validate input is a valid integer
        valid, interval = validate_int(text)
        if not valid:
            QMessageBox.warning(
                parent, 
                messages.ERROR_MESSAGES["POLL_INTERVAL_INVALID_TITLE"], 
                messages.ERROR_MESSAGES["POLL_INTERVAL_INVALID_MSG"]
            )
            return

        # Save and persist new interval
        parent.settings["poll_interval"] = interval
        ConfigManager.save(self.settings)
        log_debug(f"Saved poll interval: {interval}")

    def apply_polling_settings(self, parent):
        """
        Applies polling interval settings and restarts polling if enabled.
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
            if parent.overlay and parent.overlay.isVisible():
                parent.overlay.close()
                parent.overlay = None
                log_debug("[TabSettings] overlay turned OFF due to polling OFF")
