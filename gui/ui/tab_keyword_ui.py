# -*- coding: utf-8 -*-
"""
File: tab_keyword_ui.py
Defines the UI layout and component initialization for the TabKeyword class.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QTextEdit, QSizePolicy, QTableWidget, QSplitter
)

from gui.ui.common import create_svg_text_button
from gui.utils.utils_window import find_window_main

class TabKeywordUI:
    """
    Provides UI components and layout for the TabKeyword tab.
    """

    def init_ui(self, version_list):
        # Set up the main layout for the tab
        layout = QVBoxLayout()

        # Bible version dropdown
        self.version_box = QComboBox()
        self.version_box.addItems(version_list)

        # Keyword input field
        self.keyword_input = QLineEdit()
        self.keyword_input.returnPressed.connect(self.run_search)

        # Buttons: search, output, clear
        self.search_button = create_svg_text_button(
            "resources/svg/btn_search.svg",
            self.tr("btn_search"),
            30,
            "Search",
            self.run_search
        )
        self.select_button = create_svg_text_button(
            "resources/svg/btn_output.svg",
            self.tr("btn_output"),
            30,
            "Start slide show",
            self.save_selected_verse
        )
        self.clear_button = create_svg_text_button(
            "resources/svg/btn_clear.svg",
            self.tr("btn_clear"),
            30,
            "Stop slide show",
            self.clear_outputs
        )

        # Summary section
        self.summary_title_label = QLabel(self.tr("search_summary"))
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        self.summary_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        # Results table setup
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([self.tr("search_location"), self.tr("search_verse")])
        self.table.setColumnWidth(0, 150)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Top layout: version dropdown, keyword input, search button
        top = QHBoxLayout()
        top.addWidget(self.version_box)
        top.addWidget(self.keyword_input)
        top.addWidget(self.search_button)

        # Button layout: select and clear
        btns = QHBoxLayout()
        self.btns = btns
        btns.addWidget(self.select_button)
        btns.addWidget(self.clear_button)

        # Add top sections to main layout
        layout.addLayout(top)
        layout.addLayout(btns)

        # Bottom area: table and summary split
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.table)

        # Create summary section container
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(4, 0, 4, 0)
        bottom_layout.setSpacing(4)
        bottom_layout.addWidget(self.summary_title_label)
        bottom_layout.addWidget(self.summary_box)
        bottom_container.setLayout(bottom_layout)
        splitter.addWidget(bottom_container)

        # Assign layout ratios
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def update_button_visibility(self):
        """
        Shows or hides the select/clear buttons based on polling status.
        """
        window_main = find_window_main(self)
        if not window_main:
            return
        poll_enabled = window_main.poll_toggle_btn.isChecked()
        always_show = window_main.settings.get("always_show_on_off_buttons", False)
        effective_polling = poll_enabled or always_show

        self.select_button.setVisible(effective_polling)
        self.clear_button.setVisible(effective_polling)