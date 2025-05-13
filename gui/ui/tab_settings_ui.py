# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_settings_ui.py
Initializes the Settings tab UI for configuring fonts, themes, display output, and overlay behavior.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import qdarkstyle
import platform

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QGroupBox,
    QLineEdit, QSlider, QPushButton, QFontComboBox
)
from PySide6.QtGui import QFont

from gui.ui.common import create_button, create_svg_text_button


class TabSettingsUI:
    """
    Builds and applies the layout for the settings tab.
    Includes configuration for UI font, overlay font, display mode, and polling interval.
    """

    def init_ui(self):
        """
        Initialize the full settings UI.

        This method constructs all font-related configuration widgets, theme toggles,
        overlay settings, output paths, and polling controls.
        """
        # --------------------------
        # Main Group: App Font and Theme
        # --------------------------

        self.main_group = QGroupBox()
        self.main_group.setTitle(self.tr("setting_main_title"))
        main_layout = QVBoxLayout()

        # Label and combo for font family
        self.font_family_label = QLabel(self.tr("label_font_family"))
        self.font_family_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # OS-specific font selection
        current_font = self.app.font()
        current_family = current_font.family()
        if platform.system() == "Darwin":
            self.font_family_combo = QComboBox()
            self.font_family_combo.addItems(["Apple SD Gothic Neo", "Helvetica Neue"])
        else:
            self.font_family_combo = QFontComboBox()
            self.font_family_combo.setFontFilters(QFontComboBox.FontFilter.ScalableFonts)
        current_family = self.settings.get("font_family", "Arial")

        # Set default font
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
        self.font_weight_combo = QComboBox()
        for label, weight in [
            ("Thin", QFont.Weight.Thin), ("ExtraLight", QFont.Weight.ExtraLight),
            ("Light", QFont.Weight.Light), ("Normal", QFont.Weight.Normal),
            ("Medium", QFont.Weight.Medium), ("DemiBold", QFont.Weight.DemiBold),
            ("Bold", QFont.Weight.Bold), ("ExtraBold", QFont.Weight.ExtraBold),
            ("Black", QFont.Weight.Black)
        ]:
            self.font_weight_combo.addItem(label, weight)
        current_weight = self.settings.get("font_weight", current_font.weight())
        qt_weight = QFont.Weight(current_weight)
        for idx in range(self.font_weight_combo.count()):
            if self.font_weight_combo.itemData(idx).value == qt_weight.value:
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

        # Apply theme immediately
        if self.settings.get("dark_mode"):
            self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
        else:
            self.app.setStyleSheet("")

        # Assemble font layout
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

        # Checkbox for on/off button visibility
        self.always_on_off_checkbox = QCheckBox(self.tr("checkbox_show_on_off"))
        self.always_on_off_checkbox.setChecked(self.settings.get("always_show_on_off_buttons", False))
        self.always_on_off_checkbox.stateChanged.connect(self.apply_dynamic_settings)
        main_layout.addWidget(self.always_on_off_checkbox)

        main_layout.addStretch()
        self.main_group.setLayout(main_layout)

        # --------------------------
        # Overlay Group: Slide Display Options
        # --------------------------

        self.overlay_group = QGroupBox()
        self.overlay_group.setTitle(self.tr("setting_overlay_title"))
        overlay_layout = QVBoxLayout()

        # Display output screen
        display_layout = QHBoxLayout()
        self.display_combo = QComboBox()
        self.populate_displays()
        last_display = self.settings.get("display_index", 0)
        if last_display < self.display_combo.count():
            self.display_combo.setCurrentIndex(last_display)
        display_layout.addWidget(self.display_combo)
        overlay_layout.addLayout(display_layout)

        # Font for overlay text
        display_font_layout = QHBoxLayout()
        self.display_font_family_label = QLabel(self.tr("label_font_family"))
        display_font_layout.addWidget(self.display_font_family_label)

        if platform.system() == "Darwin":
            self.display_font_family_combo = QComboBox()
            self.display_font_family_combo.addItems(["Apple SD Gothic Neo", "Helvetica Neue"])
        else:
            self.display_font_family_combo = QFontComboBox()
            self.display_font_family_combo.setFontFilters(QFontComboBox.FontFilter.ScalableFonts)

        display_family = self.settings.get("display_font_family", "Arial")
        if isinstance(self.display_font_family_combo, QComboBox):
            self.display_font_family_combo.setCurrentText(display_family)
            self.display_font_family_combo.currentTextChanged.connect(self.apply_dynamic_settings)
        else:
            self.display_font_family_combo.setCurrentFont(QFont(display_family))
            self.display_font_family_combo.currentTextChanged.connect(self.apply_dynamic_settings)

        display_font_layout.addWidget(self.display_font_family_combo)
        display_font_layout.addStretch()

        # Font size for overlay
        self.display_font_size_label = QLabel(self.tr("label_font_size"))
        display_font_layout.addWidget(self.display_font_size_label)

        self.display_font_size_combo = QComboBox()
        font_sizes = [str(size) for size in [12, 14, 18, 24, 30, 36, 48, 60, 72, 96]]
        self.display_font_size_combo.addItems(font_sizes)
        size_index = self.display_font_size_combo.findText(str(self.settings.get("display_font_size", 36)))
        if size_index >= 0:
            self.display_font_size_combo.setCurrentIndex(size_index)
        self.display_font_size_combo.currentIndexChanged.connect(self.apply_dynamic_settings)
        display_font_layout.addWidget(self.display_font_size_combo)

        # Font weight and color for overlay
        self.display_font_weight_label = QLabel(self.tr("label_font_weight"))
        self.display_font_weight_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_font_weight_combo = QComboBox()
        for label, weight in [
            ("Thin", QFont.Weight.Thin), ("ExtraLight", QFont.Weight.ExtraLight),
            ("Light", QFont.Weight.Light), ("Normal", QFont.Weight.Normal),
            ("Medium", QFont.Weight.Medium), ("DemiBold", QFont.Weight.DemiBold),
            ("Bold", QFont.Weight.Bold), ("ExtraBold", QFont.Weight.ExtraBold),
            ("Black", QFont.Weight.Black)
        ]:
            self.display_font_weight_combo.addItem(label, weight)
        saved_weight = self.settings.get("display_font_weight", QFont.Weight.Normal.value)
        for idx in range(self.display_font_weight_combo.count()):
            if self.display_font_weight_combo.itemData(idx).value == saved_weight:
                self.display_font_weight_combo.setCurrentIndex(idx)
                break
        self.display_font_weight_combo.currentIndexChanged.connect(self.apply_dynamic_settings)
        display_font_layout.addWidget(self.display_font_weight_label)
        display_font_layout.addWidget(self.display_font_weight_combo)

        # Text color button
        self.display_font_color_label = QLabel(self.tr("label_display_font_color"))
        display_font_layout.addWidget(self.display_font_color_label)
        self.text_color_btn = create_button("")
        self.text_color_btn.setStyleSheet(f"background-color: {self.settings.get('display_text_color', '#000000')}")
        self.text_color_btn.clicked.connect(self.select_text_color)
        display_font_layout.addWidget(self.text_color_btn)
        overlay_layout.addLayout(display_font_layout)

        # Background alpha and color
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

        # Output path selector
        path_layout = QHBoxLayout()
        self.path_label = QLabel(self.tr("label_path"))
        path_layout.addWidget(self.path_label)
        self.output_edit = QLineEdit(self.verse_path)
        path_layout.addWidget(self.output_edit)
        self.browse_btn = create_svg_text_button(
            "resources/svg/btn_browse.svg", self.tr("btn_browse"), 30, "Browse location", self.select_output_path
        )
        path_layout.addWidget(self.browse_btn)
        overlay_layout.addLayout(path_layout)

        # Overlay mode and polling interval
        poll_layout = QHBoxLayout()
        self.overlay_mode_combo = QComboBox()
        self.overlay_mode_combo.addItems([self.tr("fullscreen"), self.tr("resizable")])
        mode = self.settings.get("display_overlay_mode", "fullscreen")
        self.overlay_mode_combo.setCurrentIndex(0 if mode == "fullscreen" else 1)
        self.overlay_mode_combo.currentIndexChanged.connect(self.apply_dynamic_settings)
        poll_layout.addWidget(self.overlay_mode_combo)

        poll_layout.addStretch()
        self.poll_label = QLabel(self.tr("label_poll_interval"))
        poll_layout.addWidget(self.poll_label)

        self.poll_input = QLineEdit(str(self.settings.get("poll_interval", 1000)))
        self.poll_input.setFixedHeight(self.overlay_mode_combo.sizeHint().height())
        poll_layout.addWidget(self.poll_input)

        self.poll_save = QPushButton(self.tr("btn_poll_interval_save"))
        self.poll_save.clicked.connect(self.save_poll_interval)
        poll_layout.addWidget(self.poll_save)
        overlay_layout.addLayout(poll_layout)

        # Final layout
        self.overlay_group.setLayout(overlay_layout)
        layout = QVBoxLayout()
        layout.addWidget(self.main_group)
        layout.addWidget(self.overlay_group)
        self.setLayout(layout)

        self.main_layout = main_layout
        self.overlay_layout = overlay_layout

        # Apply immediately on load
        self.apply_dynamic_settings()