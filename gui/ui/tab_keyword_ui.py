# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_keyword_ui.py
Defines the UI layout and interaction hooks for the keyword-based search tab in EuljiroBible.

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
    QTextEdit, QSizePolicy, QTableView,
    QSplitter, QRadioButton, QButtonGroup,
    QHeaderView
)

from gui.ui.common import create_svg_text_button


class TabKeywordUI:
    """
    Constructs the visual layout and widget structure for the keyword search tab.
    Provides controls for version selection, keyword input, search execution,
    result display, and slide show output.
    """

    def init_ui(self, version_list, get_polling_status, get_always_show_setting):
        """
        Initializes the UI layout and binds widget events.

        :param version_list: List of available Bible version strings
        :type version_list: list[str]
        :param get_polling_status: Callback for checking polling toggle state
        :type get_polling_status: Callable[[], bool]
        :param get_always_show_setting: Callback for checking 'always show' setting
        :type get_always_show_setting: Callable[[], bool]
        """
        self.get_polling_status = get_polling_status
        self.get_always_show_setting = get_always_show_setting

        layout = QVBoxLayout()

        # 1. Version dropdown
        self.version_box = QComboBox()
        self.version_box.addItems(version_list)
        version_row = QHBoxLayout()
        version_row.addWidget(self.version_box)
        layout.addLayout(version_row)

        # 2. Keyword input with search mode selection and button
        self.keyword_input = QLineEdit()
        self.keyword_input.returnPressed.connect(self.run_search)

        self.radio_and = QRadioButton(self.tr("search_mode_all"))  # "All words"
        self.radio_compact = QRadioButton(self.tr("search_mode_compact"))  # "Exact phrase"
        self.radio_and.setChecked(True)

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_and)
        self.radio_group.addButton(self.radio_compact)

        self.search_button = create_svg_text_button(
            "resources/svg/btn_search.svg", self.tr("btn_search"),
            30, "Search", self.run_search
        )

        search_row = QHBoxLayout()
        search_row.addWidget(self.radio_and)
        search_row.addWidget(self.radio_compact)
        search_row.addWidget(self.keyword_input)
        search_row.addWidget(self.search_button)
        layout.addLayout(search_row)

        # 3. Output & Clear buttons
        self.select_button = create_svg_text_button(
            "resources/svg/btn_output.svg", self.tr("btn_output"),
            30, "Start slide show", self.save_selected_verse
        )
        self.clear_button = create_svg_text_button(
            "resources/svg/btn_clear.svg", self.tr("btn_clear"),
            30, "Stop slide show", self.clear_outputs
        )

        btns = QHBoxLayout()
        self.btns = btns
        btns.addWidget(self.select_button)
        btns.addWidget(self.clear_button)
        layout.addLayout(btns)

        # 4. Table and summary section
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setStyleSheet("QTableView::item { padding: 6px; }")
        self.table.doubleClicked.connect(self.on_double_click_save)

        self.summary_title_label = QLabel(self.tr("search_summary"))
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        self.summary_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        bottom_container = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(4, 0, 4, 0)
        bottom_layout.setSpacing(4)
        bottom_layout.addWidget(self.summary_title_label)
        bottom_layout.addWidget(self.summary_box)
        bottom_container.setLayout(bottom_layout)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.table)
        splitter.addWidget(bottom_container)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def update_button_visibility(self):
        """
        Toggles the visibility of the Output and Clear buttons.

        Visibility is determined by polling status or the 'always show' setting.
        """
        poll_enabled = self.get_polling_status()
        always_show = self.get_always_show_setting()
        effective_polling = poll_enabled or always_show

        self.select_button.setVisible(effective_polling)
        self.clear_button.setVisible(effective_polling)

    def on_double_click_save(self, index):
        """
        Handles double-click event on the result table.

        Delegates the save logic to TabKeywordLogic.

        :param index: Clicked QModelIndex
        :type index: QModelIndex
        """
        if index.column() < 0:
            return
        self.logic.save_selected_verse(self)
