# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/ui/tab_keyword_ui.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Defines the UI layout and interaction hooks for the keyword-based search tab in EuljiroBible.
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
    UI builder mixin for the keyword search tab.

    This class constructs the widget layout and connects UI events for keyword
    searching, including version selection, keyword input, search mode toggles,
    result table display, summary output, and overlay export controls.

    The actual business logic (search, export, clearing output) is delegated to the
    owning tab class and its logic backend (e.g., TabKeyword and TabKeywordLogic).

    Attributes:
        get_polling_status (Callable[[], bool]): Callback used to determine whether
            polling mode is enabled (controls button visibility).
        get_always_show_setting (Callable[[], bool]): Callback used to determine
            whether buttons should always be shown regardless of polling state.
        version_box (QComboBox): Dropdown for selecting a Bible version.
        keyword_input (QLineEdit): Text input for search keywords.
        radio_and (QRadioButton): Search mode radio for "all words" style search.
        radio_compact (QRadioButton): Search mode radio for "exact phrase" search.
        radio_group (QButtonGroup): Radio button group for mutually exclusive modes.
        search_button (QPushButton): Button triggering a keyword search.
        select_button (QPushButton): Button exporting the selected verse.
        clear_button (QPushButton): Button clearing overlay output.
        table (QTableView): Result table view for search hits.
        summary_title_label (QLabel): Label for the summary section.
        summary_box (QTextEdit): Read-only summary output widget.
    """

    def init_ui(self, version_list, get_polling_status, get_always_show_setting):
        """
        Initialize the UI layout and bind widget events.

        Args:
            version_list (List[str]): List of available Bible version strings.
            get_polling_status (Callable[[], bool]): Callback for checking polling toggle state.
            get_always_show_setting (Callable[[], bool]): Callback for checking the
                "always show buttons" setting.
        """
        self.get_polling_status = get_polling_status
        self.get_always_show_setting = get_always_show_setting

        layout = QVBoxLayout()

        # 1. Version dropdown
        self.version_box = QComboBox()
        for version_key in version_list:
            display_name = self.bible_data.get_version_display_name(version_key)
            self.version_box.addItem(display_name, userData=version_key)
            self.version_box.setItemData(
                self.version_box.count() - 1,
                version_key,
                Qt.ToolTipRole
            )
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
        Update visibility of the Output and Clear buttons.

        Button visibility is determined by the effective polling state, defined as:
        polling enabled OR the "always show buttons" setting enabled.
        """
        poll_enabled = self.get_polling_status()
        always_show = self.get_always_show_setting()
        effective_polling = poll_enabled or always_show

        self.select_button.setVisible(effective_polling)
        self.clear_button.setVisible(effective_polling)

    def on_double_click_save(self, index):
        """
        Handle a double-click event on the result table.

        If a valid column is clicked, this delegates saving/exporting logic to the
        logic backend through the owning tab instance.

        Args:
            index (QModelIndex): Clicked table index.
        """
        if index.column() < 0:
            return
        self.logic.save_selected_verse(self)
