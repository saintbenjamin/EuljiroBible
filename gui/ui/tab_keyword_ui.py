# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_keyword_ui.py
Defines the UI layout and logic hooks for the keyword-based search tab (TabKeyword).

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
    QLabel, QLineEdit, QComboBox,
    QTextEdit, QSizePolicy, QTableWidget, 
    QSplitter, QRadioButton, QButtonGroup
)

from gui.ui.common import create_svg_text_button

class TabKeywordUI:
    """
    Constructs the keyword search tab UI layout.

    Includes version selection, keyword input, search/output/clear buttons,
    result table, and search summary area.
    """

    def init_ui(self, version_list, get_polling_status, get_always_show_setting):
        """
        Initializes the UI layout and widgets for keyword search.

        :param version_list: List of available Bible versions
        :type version_list: list[str]
        """
        self.get_polling_status = get_polling_status
        self.get_always_show_setting = get_always_show_setting

        layout = QVBoxLayout()

        # Bible version selector dropdown
        self.version_box = QComboBox()
        self.version_box.addItems(version_list)

        # Keyword input box with return key binding
        self.keyword_input = QLineEdit()
        self.keyword_input.returnPressed.connect(self.run_search)

        # Search button with SVG icon
        self.search_button = create_svg_text_button(
            "resources/svg/btn_search.svg",
            self.tr("btn_search"),
            30,
            "Search",
            self.run_search
        )

        # Slide show start button
        self.select_button = create_svg_text_button(
            "resources/svg/btn_output.svg",
            self.tr("btn_output"),
            30,
            "Start slide show",
            self.save_selected_verse
        )

        # Slide show stop button
        self.clear_button = create_svg_text_button(
            "resources/svg/btn_clear.svg",
            self.tr("btn_clear"),
            30,
            "Stop slide show",
            self.clear_outputs
        )

        # Summary label and display box
        self.summary_title_label = QLabel(self.tr("search_summary"))
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        self.summary_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        # Results table with two columns: location, verse
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([self.tr("search_location"), self.tr("search_verse")])
        self.table.setColumnWidth(0, 150)
        self.table.horizontalHeader().setStretchLastSection(True)

        # 1. Bible version selector - first row
        version_row = QHBoxLayout()
        version_row.addWidget(self.version_box)
        layout.addLayout(version_row)

        # 2. Search mode + keyword input + search button - second row
        search_row = QHBoxLayout()

        # Radio buttons for selecting search mode
        self.radio_and = QRadioButton(self.tr("search_mode_all"))       # "All words"
        self.radio_compact = QRadioButton(self.tr("search_mode_compact"))  # "Exact phrase"
        self.radio_and.setChecked(True)

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_and)
        self.radio_group.addButton(self.radio_compact)

        search_row.addWidget(self.radio_and)
        search_row.addWidget(self.radio_compact)
        search_row.addWidget(self.keyword_input)
        search_row.addWidget(self.search_button)

        layout.addLayout(search_row)

        # Button layout (select/clear)
        btns = QHBoxLayout()
        self.btns = btns
        btns.addWidget(self.select_button)
        btns.addWidget(self.clear_button)
        layout.addLayout(btns)

        # Splitter for table and summary area
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.table)

        # Bottom container with summary label and box
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(4, 0, 4, 0)
        bottom_layout.setSpacing(4)
        bottom_layout.addWidget(self.summary_title_label)
        bottom_layout.addWidget(self.summary_box)
        bottom_container.setLayout(bottom_layout)
        splitter.addWidget(bottom_container)

        # Set stretch proportions: table (3), summary (1)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def update_button_visibility(self):
        """
        Show or hide the 'Output' and 'Clear' buttons based on polling status.

        Uses global setting `always_show_on_off_buttons` or the toggle state.
        """

        # Check polling or always-show flag
        poll_enabled = self.get_polling_status()
        always_show = self.get_always_show_setting()
        effective_polling = poll_enabled or always_show

        # Adjust button visibility accordingly
        self.select_button.setVisible(effective_polling)
        self.clear_button.setVisible(effective_polling)