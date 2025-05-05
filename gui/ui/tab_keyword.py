# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/ui/tab_keyword.py
Implements the TabKeyword for EuljiroBible, enabling Bible keyword search, result display, and verse export.

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
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QTextEdit, QMessageBox, QSizePolicy, QTableWidget, QSplitter, QTableWidgetItem
)

from core.utils.utils_bible import (
    search_keywords, keyword_counts
)
from core.utils.bible_data_loader import BibleDataLoader
from core.utils.logger import log_debug
from core.utils.utils_bible import normalize_book_name, compact_book_id
from core.utils.utils_output import format_output, save_to_files
from gui.ui.common import create_svg_text_button
from gui.ui.locale.message_loader import load_messages
from gui.utils.utils_window import find_window_main

class TabKeyword(QWidget):
    """
    Tab for searching Bible verses by keywords, displaying results, and exporting selected verses.
    """

    def __init__(self, version_list, settings, tr):
        """
        Initializes the TabKeyword.

        Args:
            version_list (list): List of available Bible versions.
            settings (dict): Loaded user settings.
            tr (function): Translation function.
        """
        super().__init__()
        self.tr = tr     # Translation function for UI strings
        self.settings = settings  # Loaded configuration settings
        self.init_ui(version_list=version_list)

    def init_ui(self, version_list):
        # Set up the main layout for the tab
        layout = QVBoxLayout()
        self.current_language = "ko"
        self.bible_data = BibleDataLoader()  # Load Bible metadata

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

    def run_search(self):
        """
        Executes a keyword search in the selected version.
        Populates table and summary with results.
        """
        log_debug("[TabKeyword] run_search started")
        version = self.version_box.currentText()
        keywords = self.keyword_input.text().strip().split()

        # Validate keyword input
        if not keywords or all(k == "" for k in keywords):
            QMessageBox.warning(self, 
                self.tr("warn_input_title"), 
                self.tr("warn_input_msg"))
            return

        # Perform search and generate summary
        results = search_keywords(self.bible_data, version, keywords)
        counts = keyword_counts(results, keywords)

        self.update_table(results)
        self.update_summary(counts)
        log_debug(f"[TabKeyword] search results: {len(results)} found")

        # Add count to summary box
        self.summary_box.append("")  # spacing
        self.summary_box.append(f"{self.tr('total_results_label')} {len(results)}")

        if not results:
            QMessageBox.information(self, 
                self.tr("info_no_results_title"), 
                self.tr("info_no_results_msg"))

    def change_language(self, lang_code):
        """
        Changes the UI language dynamically.

        Args:
            lang_code (str): Language code.
        """
        self.current_language = lang_code
        self.messages = load_messages(lang_code)
        self.keyword_input.setPlaceholderText(self.tr("search_keyword_hint"))
        self.search_button.setText(self.tr("btn_search"))
        self.select_button.setText(self.tr("btn_output"))
        self.clear_button.setText(self.tr("btn_clear"))
        self.table.setHorizontalHeaderLabels([self.tr("search_location"), self.tr("search_verse")])
        self.summary_title_label.setText(self.tr("search_summary"))
        self.summary_box.setPlaceholderText(self.tr("search_summary"))

    def save_selected_verse(self):
        """
        Saves the currently selected verse from search results.
        """
        log_debug("[TabKeyword] save_selected_verse called")
        row = self.table.currentRow()
        if row >= 0:
            ref = self.table.item(row, 0).text()

            # Extract book, chapter, and verse from selected reference
            book_str, chap_verse = ref.rsplit(' ', 1)
            book = normalize_book_name(book_str, self.bible_data, self.current_language)
            chapter, verse = chap_verse.split(':')
            chapter = int(chapter)
            verse = int(verse) 

            normalized = compact_book_id(book)
            version = self.version_box.currentText()
            verses = self.bible_data.get_verses(version)

            # Resolve canonical book name
            book = normalized
            if book not in verses:
                for key in verses:
                    if key.lower().replace(" ", "") == book.lower().replace(" ", ""):
                        book = key
                        break
                else:
                    log_debug(f"[TabKeyword] Book '{book}' not found in version {version}")
                    QMessageBox.warning(self, self.tr("warn_no_chapter_title"), self.tr("warn_no_chapter_msg").format(normalized, chapter))
                    return

            # Create output and save
            verse_range = (verse, verse)
            book_alias = self.bible_data.get_book_alias(self.current_language)
            version_alias = self.bible_data.get_version_alias(self.current_language)

            merged = format_output(
                [version],
                book,
                str(chapter),
                verse_range,
                {version: verses},
                self.tr,
                for_whitebox=True,
                lang_code=self.current_language,
                bible_data=self.bible_data,
                book_alias=book_alias,
                version_alias=version_alias
            )

            try:
                save_to_files(merged, self.settings)
                log_debug("[TabKeyword] selected verse saved successfully")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("error_saving_title"),
                    self.tr("error_saving_msg").format(e)
                )
        else:
            # No row selected
            QMessageBox.warning(
                self,
                self.tr("warn_selection_title"),
                self.tr("warn_selection_msg")
            )

    def clear_outputs(self):
        """
        Clears output files.
        """
        save_to_files("", self.settings)

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

    def update_table(self, results):
        """
        Updates the search results table with found verses.

        Args:
            results (list): List of search result entries.
        """
        self.table.setRowCount(0)
        for i, res in enumerate(results):
            self.table.insertRow(i)

            display_book = self.bible_data.get_standard_book(res['book'], self.current_language)
            ref_item = QTableWidgetItem(f"{display_book} {res['chapter']}:{res['verse']}")
            ref_item.setFont(self.table.font())
            ref_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            ref_item.setFlags(ref_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, ref_item)

            item = QTableWidgetItem(res['text'])
            item.setFont(self.table.font())
            item.setToolTip(res['highlighted'])
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)

        self.table.setWordWrap(True)
        self.table.resizeRowsToContents()

    def update_summary(self, counts):
        """
        Updates the keyword counts summary box.

        Args:
            counts (dict): Dictionary mapping keywords to their counts.
        """
        self.summary_box.setPlainText("\n".join(f"{k}: {v}" for k, v in counts.items()))