# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_keyword_logic.py
Handles the keyword search, result display, and verse saving logic for the TabKeyword UI.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from core.utils.bible_keyword_searcher import BibleKeywordSearcher
from core.utils.bible_parser import resolve_book_name
from core.utils.logger import log_debug
from core.utils.utils_output import format_output, save_to_files

from gui.utils.keyword_result_model import KeywordResultTableModel
from gui.utils.keyword_highlight_delegate import KeywordHighlightDelegate


class TabKeywordLogic:
    """
    Provides backend logic for keyword-based search, result formatting,
    and verse saving for the TabKeyword UI.
    """

    def __init__(self, settings, tr_func):
        """
        Initializes the logic handler with settings and translation function.

        :param settings: Global application settings
        :type settings: dict
        :param tr_func: Translation function for localized strings
        :type tr_func: Callable[[str], str]
        """
        self.settings = settings
        self.tr = tr_func

    def run_search(self, parent):
        """
        Performs a keyword search and updates the result table and summary.

        :param parent: The TabKeyword instance (UI context)
        :type parent: QWidget
        """
        log_debug("[TabKeyword] run_search started")
        version = parent.version_box.currentText()
        keywords = parent.keyword_input.text().strip().split()

        if not keywords or all(k == "" for k in keywords):
            QMessageBox.warning(parent, self.tr("warn_input_title"), self.tr("warn_input_msg"))
            return

        # Determine search mode from radio buttons
        mode = "compact" if parent.radio_compact.isChecked() else "and"

        # Execute search
        searcher = BibleKeywordSearcher(version)
        results = searcher.search(" ".join(keywords), mode=mode)
        counts = searcher.count_keywords(results, keywords)

        parent.update_table(results)
        parent.update_summary(counts)

        log_debug(f"[TabKeyword] search results: {len(results)} found")

        parent.summary_box.append("")  # add spacing line
        parent.summary_box.append(f"{self.tr('total_results_label')} {len(results)}")

        if not results:
            QMessageBox.information(parent, self.tr("info_no_results_title"), self.tr("info_no_results_msg"))

    def save_selected_verse(self, parent):
        """
        Saves the currently selected verse in the result table to verse_output.txt.

        :param parent: The TabKeyword instance
        :type parent: QWidget
        """
        log_debug("[TabKeyword] save_selected_verse called")

        index = parent.table.currentIndex()
        row = index.row()
        if row < 0:
            QMessageBox.warning(parent, self.tr("warn_selection_title"), self.tr("warn_selection_msg"))
            return

        model = parent.table.model()
        ref = model.index(row, 1).data()  # Get reference string like "John 3:16"

        try:
            book_str, chap_verse = ref.rsplit(' ', 1)
            book = resolve_book_name(book_str) or book_str
            chapter, verse = chap_verse.split(':')
            chapter = int(chapter)
            verse = int(verse)
        except Exception as e:
            log_debug(f"[TabKeyword] Failed to parse reference: {ref}")
            QMessageBox.warning(parent, self.tr("warn_selection_title"), self.tr("warn_selection_msg"))
            return

        normalized = book.replace(" ", "")
        version = parent.version_box.currentText()
        verses = parent.bible_data.get_verses(version)

        # Normalize book name if needed
        if normalized not in verses:
            for key in verses:
                if key.lower().replace(" ", "") == normalized.lower():
                    normalized = key
                    break
            else:
                log_debug(f"[TabKeyword] Book '{book}' not found in version {version}")
                QMessageBox.warning(
                    parent,
                    self.tr("warn_no_chapter_title"),
                    self.tr("warn_no_chapter_msg").format(normalized, chapter)
                )
                return

        verse_range = (verse, verse)
        book_alias = parent.bible_data.get_book_alias(parent.current_language)
        version_alias = parent.bible_data.get_version_alias(parent.current_language)

        merged = format_output(
            [version],
            normalized,
            str(chapter),
            verse_range,
            {version: verses},
            self.tr,
            for_whitebox=True,
            lang_code=parent.current_language,
            bible_data=parent.bible_data,
            book_alias=book_alias,
            version_alias=version_alias
        )

        try:
            save_to_files(merged, parent.settings)
            log_debug("[TabKeyword] selected verse saved successfully")
        except Exception as e:
            QMessageBox.critical(parent, self.tr("error_saving_title"), self.tr("error_saving_msg").format(e))

    def clear_outputs(self, parent):
        """
        Clears the verse output file by writing an empty string.

        :param parent: TabKeyword instance
        :type parent: QWidget
        """
        save_to_files("", parent.settings)

    def update_table(self, parent, results):
        """
        Sets the result table model and installs a keyword highlight delegate.

        :param parent: TabKeyword instance
        :type parent: QWidget
        :param results: List of verse entry dictionaries
        :type results: list[dict]
        """
        model = KeywordResultTableModel(results, parent.bible_data, parent.current_language, parent.tr)
        parent.table.setModel(model)

        keywords = parent.keyword_input.text().strip().split()
        delegate = KeywordHighlightDelegate(keywords)
        parent.table.setItemDelegateForColumn(2, delegate)

        parent.table.resizeColumnsToContents()
        parent.table.resizeRowsToContents()
        parent.table.setStyleSheet("QTableView::item { padding: 6px; }")

    def update_summary(self, parent, counts):
        """
        Updates the summary box with the count of each keyword found.

        :param parent: TabKeyword instance
        :type parent: QWidget
        :param counts: Dictionary mapping keyword → count
        :type counts: dict[str, int]
        """
        parent.summary_box.setPlainText("\n".join(f"{k}: {v}" for k, v in counts.items()))
