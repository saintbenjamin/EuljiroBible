# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_verse_ui.py
Builds the TabVerse UI layout and handles basic input/output interactions.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QComboBox, QTextEdit, QScrollArea,
    QGridLayout, QSplitter, QMessageBox
)
from PySide6.QtGui import QStandardItemModel

from gui.ui.common import create_svg_text_button, LoadingIndicator


class TabVerseUI:
    """
    Provides the full layout for the TabVerse interface.

    Contains UI components for version selection, book/chapter/verse input,
    and buttons to display, save, or clear verse text.
    """

    def init_ui(self, version_list):
        """
        Initializes the full verse tab interface layout.

        :param version_list: List of Bible versions to populate as checkboxes
        :type version_list: list[str]
        """
        # Scrollable checkbox grid for Bible versions
        self.version_scroll = QScrollArea()
        self.version_scroll.setWidgetResizable(True)
        self.version_widget = QWidget()
        self.version_layout = QGridLayout(self.version_widget)
        self.version_scroll.setWidget(self.version_widget)

        # Add version checkboxes dynamically
        for version in enumerate(version_list):
            if isinstance(version, tuple):
                _, version_name = version
            else:
                version_name = version
            checkbox = self.selection_manager.create_version_checkbox(self, version_name)
            self.version_layout.addWidget(checkbox)

        # Adjust grid layout
        self.selection_manager.update_grid_layout(self)

        # Internal UI state
        self.enter_state = 0
        self.use_alias = False

        # Toggle button for alias/full version names
        self.alias_toggle_btn = QPushButton(self.tr("label_alias_full"))
        self.alias_toggle_btn.setCheckable(True)
        self.alias_toggle_btn.setChecked(False)
        self.alias_toggle_btn.clicked.connect(self.toggle_alias_mode)

        # Label summarizing selected versions
        self.version_summary_label = QLabel(self.tr("msg_nothing"))
        version_label_layout = QHBoxLayout()
        version_label_layout.addWidget(self.alias_toggle_btn)
        version_label_layout.addWidget(self.version_summary_label)
        version_label_layout.addStretch()

        # Labels for input fields
        self.book_label = QLabel(self.tr("label_book"))
        self.chapter_label = QLabel(self.tr("label_chapter"))
        self.verse_label = QLabel(self.tr("label_verse"))

        # Book dropdown with inline editing
        self.book_combo = QComboBox()
        self.book_combo.setModel(QStandardItemModel(self.book_combo))
        self.book_combo.setEditable(True)
        self.book_combo.setInsertPolicy(QComboBox.NoInsert)

        # Chapter and verse inputs
        self.chapter_input = QComboBox()
        self.chapter_input.setEditable(True)
        self.chapter_input.lineEdit().returnPressed.connect(self.handle_enter)

        self.verse_input = QLineEdit()
        self.verse_input.setPlaceholderText(self.tr("verse_input_hint"))
        self.verse_input.returnPressed.connect(self.handle_enter)

        # Action buttons
        self.search_btn = create_svg_text_button(
            "resources/svg/btn_search.svg",
            self.tr("btn_search"),
            30,
            "Search",
            self._on_display_verse
        )
        self.save_btn = create_svg_text_button(
            "resources/svg/btn_output.svg",
            self.tr("btn_output"),
            30,
            "Start slide show",
            self._on_save_verse
        )
        self.clear_display_btn = create_svg_text_button(
            "resources/svg/btn_clear.svg",
            self.tr("btn_clear"),
            30,
            "Stop slide show",
            self.clear_outputs
        )
        self.prev_verse_btn = create_svg_text_button(
            "resources/svg/btn_prev.svg",
            self.tr("btn_prev"),
            30,
            "Go to previous verse",
            lambda: self.shift_verse(-1)
        )
        self.next_verse_btn = create_svg_text_button(
            "resources/svg/btn_next.svg",
            self.tr("btn_next"),
            30,
            "Go to next verse",
            lambda: self.shift_verse(1)
        )

        # Layout for book/chapter/verse input
        input_layout = QHBoxLayout()
        self.input_layout = input_layout
        input_layout.addWidget(self.book_label)
        input_layout.addWidget(self.book_combo)
        input_layout.addWidget(self.chapter_label)
        input_layout.addWidget(self.chapter_input)
        input_layout.addWidget(self.verse_label)
        input_layout.addWidget(self.verse_input)

        # Adjust input field stretch ratios
        input_layout.setStretch(1, 2)
        input_layout.setStretch(3, 1)
        input_layout.setStretch(5, 1)

        # Button row layout
        button_layout = QHBoxLayout()
        self.button_layout = button_layout
        button_layout.addWidget(self.prev_verse_btn)
        button_layout.addWidget(self.search_btn)
        poll_enabled = self.settings.get("poll_enabled", False)
        if poll_enabled:
            button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.next_verse_btn)
        if poll_enabled:
            button_layout.addWidget(self.clear_display_btn)

        # Add button row to the input layout
        input_layout.addLayout(button_layout)

        # Display box for output
        self.display_box = QTextEdit()
        self.display_box.setReadOnly(True)

        # Loading indicator overlay
        self.loading_indicator = LoadingIndicator(self.display_box.viewport())
        self.loading_indicator.hide()

        # Lower panel combining input and display
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.addLayout(input_layout)
        bottom_layout.addWidget(self.display_box)

        # Splitter between version list and display panel
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.version_scroll)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([150, 400])

        # Final layout
        layout = QVBoxLayout()
        layout.addLayout(version_label_layout)
        layout.addWidget(splitter)

        self.setLayout(layout)

        # Add loading animation widget last
        layout.addWidget(self.loading_indicator)

    def _on_display_verse(self):
        """
        Trigger display of Bible verse when Search button is clicked.

        Uses `self.get_reference`, `self.verse_input`, and `self.apply_output_text`.
        """
        output = self.logic.display_verse(
            self.get_reference,
            self.verse_input,
            self.apply_output_text
        )
        if output:
            self.formatted_verse_text = output

    def _on_save_verse(self):
        """
        Saves the currently displayed verse.

        Invoked by the Save button; shows critical dialog on error.
        """
        try:
            self.logic.save_verse(self.formatted_verse_text)
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("error_output_title"),
                self.tr("error_output_msg").format(str(e))
            )