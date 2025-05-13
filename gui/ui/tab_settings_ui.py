# External libraries
import qdarkstyle
import platform

# PySide6 modules
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QCheckBox, QGroupBox, 
    QLineEdit, QSlider, QPushButton
)
from PySide6.QtGui import QFont

# Common UI elements
from gui.ui.common import create_button, create_svg_text_button

class TabSettingsUI:
    def init_ui(self):
        """
        Initializes the UI layout for settings tab.
        """
        
        # --- Main Settings Group ---

        self.main_group = QGroupBox()
        self.main_group.setTitle(self.tr("setting_main_title"))
        main_layout = QVBoxLayout()

        # Font family label
        self.font_family_label = QLabel(self.tr("label_font_family"))
        self.font_family_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Font family combo setup
        current_font = self.app.font()
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
        if self.settings.get("dark_mode"):
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

        display_font = self.app.font()
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