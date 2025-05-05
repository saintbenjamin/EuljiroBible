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

# External libraries
import qdarkstyle
import platform

# PySide6 modules
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QMessageBox,
    QCheckBox, QGroupBox, QLineEdit,
    QApplication, QSlider, QPushButton
)
from PySide6.QtGui import QFont

# Core utilities
from core.utils.file_helpers import should_show_overlay
from core.utils.input_validators import validate_int
from core.utils.logger import log_debug

# GUI config and constants
from gui.config.config_manager import ConfigManager
from gui.constants import messages

# Common UI elements
from gui.ui.common import create_button, create_svg_text_button

# Localization
from gui.ui.locale.message_loader import load_messages

# Overlay logic
from gui.utils.overlay_factory import create_overlay
from gui.utils.settings_helper import update_overlay_settings

# Dialog utilities
from gui.utils.utils_dialog import get_save_path, set_color_from_dialog

# Display/font/theme/window helpers
from gui.utils.utils_display import get_display_descriptions
from gui.utils.utils_fonts import apply_main_font_to_app, apply_overlay_font
from gui.utils.utils_theme import set_dark_mode, refresh_main_tabs
from gui.utils.utils_window import find_window_main

class TabSettings(QWidget):
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

        # --- Main Settings Group ---

        self.main_group = QGroupBox()
        self.main_group.setTitle(self.tr("setting_main_title"))
        main_layout = QVBoxLayout()

        # Font family label
        self.font_family_label = QLabel(self.tr("label_font_family"))
        self.font_family_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Font family combo setup
        current_font = app.font()
        current_family = current_font.family()
        if platform.system() == "Darwin":
            self.font_family_combo = QComboBox()
            safe_fonts = ["Apple SD Gothic Neo", "Helvetica Neue"]
            self.font_family_combo.addItems(safe_fonts)
        else:
            from PySide6.QtWidgets import QFontComboBox
            self.font_family_combo = QFontComboBox()
            self.font_family_combo.setFontFilters(QFontComboBox.FontFilter.ScalableFonts)
        current_family = self.settings.get("font_family", "Arial")

        # Set font family selection
        if isinstance(self.font_family_combo, QComboBox):
            self.font_family_combo.setCurrentText(current_family)
            self.font_family_combo.currentTextChanged.connect(self.apply_dynamic_settings)
        else:
            self.font_family_combo.setCurrentFont(QFont(current_family))
            self.font_family_combo.currentFontChanged.connect(self.apply_dynamic_settings)

        # Font size selection
        self.font_size_label = QLabel(self.tr("label_font_size"))
        self.font_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        current_size = current_font.pointSize()
        self.font_size_combo = QComboBox()
        for size in range(6, 49, 2):
            self.font_size_combo.addItem(str(size))
        self.font_size_combo.setCurrentText(str(current_size))
        self.font_size_combo.currentIndexChanged.connect(self.apply_dynamic_settings)

        # Font weight selection
        self.font_weight_label = QLabel(self.tr("label_font_weight"))
        self.font_weight_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        current_weight = self.settings.get("font_weight", current_font.weight())
        qt_weight = QFont.Weight(current_weight)
        self.font_weight_combo = QComboBox()
        self.font_weight_combo.addItem("Thin", QFont.Weight.Thin)
        self.font_weight_combo.addItem("ExtraLight", QFont.Weight.ExtraLight)
        self.font_weight_combo.addItem("Light", QFont.Weight.Light)
        self.font_weight_combo.addItem("Normal", QFont.Weight.Normal)
        self.font_weight_combo.addItem("Medium", QFont.Weight.Medium)
        self.font_weight_combo.addItem("DemiBold", QFont.Weight.DemiBold)
        self.font_weight_combo.addItem("Bold", QFont.Weight.Bold)
        self.font_weight_combo.addItem("ExtraBold", QFont.Weight.ExtraBold)
        self.font_weight_combo.addItem("Black", QFont.Weight.Black)
        for idx in range(self.font_weight_combo.count()):
            item_weight = self.font_weight_combo.itemData(idx)
            if item_weight.value == qt_weight.value:
                self.font_weight_combo.setCurrentIndex(idx)
                break
        self.font_weight_combo.currentIndexChanged.connect(self.apply_dynamic_settings)

        # Theme toggle button
        self.theme_toggle_btn = create_svg_text_button(
            "resources/svg/btn_theme_toggle.svg",
            self.tr("btn_theme_toggle"),
            30,
            "Toggle Light/Dark Theme",
            self.toggle_theme
        )

        # Apply initial theme
        if settings.get("dark_mode"):
            self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
        else:
            self.app.setStyleSheet("")

        # Layouts for font selection
        main_fonts = QHBoxLayout()
        main_fonts.addWidget(self.font_family_label)
        main_fonts.addWidget(self.font_family_combo)
        main_fonts.addWidget(self.font_size_label)
        main_fonts.addWidget(self.font_size_combo)
        main_fonts.addWidget(self.font_weight_label)
        main_fonts.addWidget(self.font_weight_combo)
        main_layout.addLayout(main_fonts)

        dark_toggle = QHBoxLayout()
        dark_toggle.addWidget(self.theme_toggle_btn)
        main_layout.addLayout(dark_toggle)

        # Checkbox to always show on/off buttons
        self.always_on_off_checkbox = QCheckBox(self.tr("checkbox_show_on_off"))
        self.always_on_off_checkbox.setChecked(self.settings.get("always_show_on_off_buttons", False))
        self.always_on_off_checkbox.stateChanged.connect(self.apply_dynamic_settings)
        main_layout.addWidget(self.always_on_off_checkbox)

        main_layout.addStretch()
        self.main_group.setLayout(main_layout)

        # --- Overlay Settings Group ---

        self.overlay_group = QGroupBox()
        self.overlay_group.setTitle(self.tr("setting_overlay_title"))

        overlay_layout = QVBoxLayout()

        # --- Display output screen selector ---
        display_layout = QHBoxLayout()
        self.display_combo = QComboBox()
        self.populate_displays()
        last_display = self.settings.get("display_index", 0)
        if last_display < self.display_combo.count():
            self.display_combo.setCurrentIndex(last_display)
        display_layout.addWidget(self.display_combo)
        overlay_layout.addLayout(display_layout)

        # --- Display font configuration ---
        display_font_layout = QHBoxLayout()
        self.display_font_family_label = QLabel(self.tr("label_font_family"))
        display_font_layout.addWidget(self.display_font_family_label)

        display_font = app.font()
        display_family = display_font.family()

        # Choose font family widget depending on OS
        if platform.system() == "Darwin":
            self.display_font_family_combo = QComboBox()
            safe_display_fonts = ["Apple SD Gothic Neo", "Helvetica Neue"]
            self.display_font_family_combo.addItems(safe_display_fonts)
        else:
            self.display_font_family_combo = QFontComboBox()
            self.display_font_family_combo.setFontFilters(QFontComboBox.FontFilter.ScalableFonts)

        # Set default font
        display_family = self.settings.get("display_font_family", "Arial")
        if isinstance(self.display_font_family_combo, QComboBox):
            self.display_font_family_combo.setCurrentText(display_family)
            self.display_font_family_combo.currentTextChanged.connect(self.apply_dynamic_settings)
        else:
            self.display_font_family_combo.setCurrentFont(QFont(display_family))
            self.display_font_family_combo.currentTextChanged.connect(self.apply_dynamic_settings)

        display_font_layout.addWidget(self.display_font_family_combo)
        display_font_layout.addStretch()

        # --- Display font size ---
        self.display_font_size_label = QLabel(self.tr("label_font_size"))
        display_font_layout.addWidget(self.display_font_size_label)

        self.display_font_size_combo = QComboBox()
        font_sizes = [str(size) for size in [12, 14, 18, 24, 30, 36, 48, 60, 72, 96]]
        self.display_font_size_combo.addItems(font_sizes)

        current_display_size = str(self.settings.get("display_font_size", 36))
        index = self.display_font_size_combo.findText(current_display_size)
        if index >= 0:
            self.display_font_size_combo.setCurrentIndex(index)

        self.display_font_size_combo.currentIndexChanged.connect(self.apply_dynamic_settings)
        display_font_layout.addWidget(self.display_font_size_combo)
        display_font_layout.addStretch()

        # --- Display font weight ---
        self.display_font_weight_label = QLabel(self.tr("label_font_weight"))
        self.display_font_weight_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_font_weight_combo = QComboBox()
        self.display_font_weight_combo.addItem("Thin", QFont.Weight.Thin)
        self.display_font_weight_combo.addItem("ExtraLight", QFont.Weight.ExtraLight)
        self.display_font_weight_combo.addItem("Light", QFont.Weight.Light)
        self.display_font_weight_combo.addItem("Normal", QFont.Weight.Normal)
        self.display_font_weight_combo.addItem("Medium", QFont.Weight.Medium)
        self.display_font_weight_combo.addItem("DemiBold", QFont.Weight.DemiBold)
        self.display_font_weight_combo.addItem("Bold", QFont.Weight.Bold)
        self.display_font_weight_combo.addItem("ExtraBold", QFont.Weight.ExtraBold)
        self.display_font_weight_combo.addItem("Black", QFont.Weight.Black)

        # Set saved weight as current
        saved_weight = self.settings.get("display_font_weight", QFont.Weight.Normal.value)
        qt_weight = QFont.Weight(saved_weight)
        for idx in range(self.display_font_weight_combo.count()):
            item_weight = self.display_font_weight_combo.itemData(idx)
            if item_weight.value == qt_weight.value:
                self.display_font_weight_combo.setCurrentIndex(idx)
                break

        self.display_font_weight_combo.currentIndexChanged.connect(self.apply_dynamic_settings)
        display_font_layout.addWidget(self.display_font_weight_label)
        display_font_layout.addWidget(self.display_font_weight_combo)
        display_font_layout.addStretch()

        # --- Display font color ---
        self.display_font_color_label = QLabel(self.tr("label_display_font_color"))
        display_font_layout.addWidget(self.display_font_color_label)

        self.text_color_btn = create_button("")
        self.text_color_btn.setStyleSheet(f"background-color: {self.settings.get('display_text_color', '#000000')}")
        self.text_color_btn.clicked.connect(self.select_text_color)
        display_font_layout.addWidget(self.text_color_btn)

        overlay_layout.addLayout(display_font_layout)

        # --- Background settings: alpha & color ---
        bg_layout = QHBoxLayout()

        self.bg_alpha_label = QLabel(self.tr("label_display_bg_alpha"))
        bg_layout.addWidget(self.bg_alpha_label)

        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setRange(0, 100)
        self.alpha_slider.setValue(int(self.settings.get("display_bg_alpha", 0.85) * 100))
        self.alpha_slider.valueChanged.connect(self.apply_dynamic_settings)
        bg_layout.addWidget(self.alpha_slider)

        self.bg_color_label = QLabel(self.tr("label_display_bg_color"))
        bg_layout.addWidget(self.bg_color_label)

        self.bg_color_btn = create_button("")
        self.bg_color_btn.setStyleSheet(f"background-color: {self.settings.get('display_bg_color', '#FFFFFF')}")
        self.bg_color_btn.clicked.connect(self.select_bg_color)
        bg_layout.addWidget(self.bg_color_btn)

        overlay_layout.addLayout(bg_layout)

        # --- Output file path ---
        path_layout = QHBoxLayout()
        self.path_label = QLabel(self.tr("label_path"))
        path_layout.addWidget(self.path_label)

        self.output_edit = QLineEdit(self.verse_path)
        path_layout.addWidget(self.output_edit)

        self.browse_btn = create_svg_text_button(
            "resources/svg/btn_browse.svg",
            self.tr("btn_browse"),
            30,
            "Browse location",
            self.select_output_path
        )
        path_layout.addWidget(self.browse_btn)
        overlay_layout.addLayout(path_layout)

        # --- Polling interval and overlay mode ---
        poll_layout = QHBoxLayout()

        self.overlay_mode_combo = QComboBox()
        self.overlay_mode_combo.addItems([
            self.tr("fullscreen"),
            self.tr("resizable")
        ])
        mode = self.settings.get("display_overlay_mode", "fullscreen")
        self.overlay_mode_combo.setCurrentIndex(0 if mode == "fullscreen" else 1)
        self.overlay_mode_combo.currentIndexChanged.connect(self.apply_dynamic_settings)
        poll_layout.addWidget(self.overlay_mode_combo)

        poll_layout.addStretch()

        self.poll_label = QLabel(self.tr("label_poll_interval"))
        self.poll_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        poll_layout.addWidget(self.poll_label)

        self.poll_input = QLineEdit(str(self.settings.get("poll_interval", 1000)))
        self.poll_input.setFixedHeight(self.overlay_mode_combo.sizeHint().height())
        poll_layout.addWidget(self.poll_input)

        self.poll_save = QPushButton(self.tr("btn_poll_interval_save"))
        self.poll_save.clicked.connect(self.save_poll_interval)
        poll_layout.addWidget(self.poll_save)

        overlay_layout.addLayout(poll_layout)

        # Apply final layout
        self.overlay_group.setLayout(overlay_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.main_group)
        layout.addWidget(self.overlay_group)
        self.setLayout(layout)

        # Save layout references
        self.main_layout = main_layout
        self.overlay_layout = overlay_layout

        # Apply settings immediately
        self.apply_dynamic_settings()

    def populate_displays(self):
        """
        Populates the display dropdown with available screens.
        """
        self.display_combo.clear()
        self.display_combo.addItems(get_display_descriptions())

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

    def apply_dynamic_settings(self):
        """
        Applies font, overlay, style settings, and updates button visibility dynamically.
        """
        if not hasattr(self, "display_font_size_combo"):
            return

        # Apply main font to the entire application
        apply_main_font_to_app(
            self.font_family_combo.currentText(),
            int(self.font_size_combo.currentText()),
            self.font_weight_combo.currentData(),
            self.window()
        )

        # Update overlay settings dictionary from current widgets
        updated_overlay = update_overlay_settings(self.settings, {
            "font_family_combo": self.display_font_family_combo,
            "font_size_combo": self.display_font_size_combo,
            "font_weight_combo": self.display_font_weight_combo,
            "alpha_slider": self.alpha_slider,
            "text_color_btn": self.text_color_btn,
            "bg_color_btn": self.bg_color_btn,
            "mode_combo": self.overlay_mode_combo
        })

        # Save overlay settings to config
        ConfigManager.update_partial(updated_overlay)

        # Save toggle state of ON/OFF visibility setting
        always_show_on_off = self.always_on_off_checkbox.isChecked()
        ConfigManager.update_partial({"always_show_on_off_buttons": always_show_on_off})
        self.settings["always_show_on_off_buttons"] = always_show_on_off

        # Reapply font to overlay if visible
        if self.overlay:
            apply_overlay_font(self.overlay, self.settings)

        # Reload settings into the main window and refresh all tabs
        window_main = find_window_main(self)
        if window_main:
            window_main.settings = ConfigManager.load()
            refresh_main_tabs(window_main)

    def apply_font_to_children(self, widget, font):
        """
        Recursively applies the font to all child widgets.

        Args:
            widget (QWidget): Parent widget.
            font (QFont): Font to apply.
        """
        widget.setFont(font)
        for child in widget.findChildren(QWidget):
            child.setFont(font)

    def select_text_color(self):
        """
        Opens a color dialog to select the overlay text color.

        On valid color selection, updates the button style,
        saves the selected color to settings, and reapplies dynamic settings.
        """
        set_color_from_dialog(self.text_color_btn, "display_text_color", self.apply_dynamic_settings)

    def select_bg_color(self):
        """
        Opens a color dialog to select the overlay background color.

        On valid color selection, updates the button style,
        saves the selected color to settings, and reapplies dynamic settings.
        """
        set_color_from_dialog(self.bg_color_btn, "display_bg_color", self.apply_dynamic_settings)

    def select_output_path(self):
        """
        Opens a file dialog to select output path for verse output.
        """
        current_path = self.output_edit.text()
        path = get_save_path(self, current_path, self.tr("dialog_path"))
        if path:
            self.output_edit.setText(path)
            self.settings["output_path"] = path
            ConfigManager.update_partial({"output_path": path})

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
                # Ask user for confirmation on single-display setup
                log_debug("[TabSettings] about to ask single-display warning")
                reply = QMessageBox.question(
                    self,
                    self.tr("warning_single_display_title"),
                    self.tr("warning_single_display_msg"),
                    QMessageBox.Yes | QMessageBox.No
                )
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

    def apply_polling_settings(self):
        """
        Applies polling interval settings and restarts polling if enabled.
        """
        poll_enabled = self.settings.get("poll_enabled", False)
        poll_interval = self.settings.get("poll_interval", 1000)

        if poll_enabled:
            if self.poll_timer.isActive():
                self.poll_timer.stop()
            self.poll_timer.start(poll_interval)
            log_debug("[TabSettings] polling restarted")
            self.poll_file()
        else:
            if self.poll_timer.isActive():
                self.poll_timer.stop()
            log_debug("[TabSettings] polling stopped")
            if self.overlay and self.overlay.isVisible():
                self.overlay.close()
                self.overlay = None
                log_debug("[TabSettings] overlay turned OFF due to polling OFF")

    def save_poll_interval(self):
        """
        Saves the polling interval for overlay updates.

        Validates that the entered value is an integer.
        On success, updates the settings and saves them to disk.
        If invalid, shows a warning message box to the user.
        """
        text = self.poll_input.text()

        # Validate input is a valid integer
        valid, interval = validate_int(text)
        if not valid:
            QMessageBox.warning(
                self, 
                messages.ERROR_MESSAGES["POLL_INTERVAL_INVALID_TITLE"], 
                messages.ERROR_MESSAGES["POLL_INTERVAL_INVALID_MSG"]
            )
            return

        # Save and persist new interval
        self.settings["poll_interval"] = interval
        ConfigManager.save(self.settings)
        log_debug(f"Saved poll interval: {interval}")


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