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
from PySide6.QtWidgets import QTableWidgetItem, QMessageBox

from core.utils.bible_keyword_searcher import BibleKeywordSearcher
from core.utils.bible_parser import resolve_book_name
from core.utils.logger import log_debug
from core.utils.utils_output import format_output, save_to_files


class TabKeywordLogic:
    """
    Provides backend logic for keyword-based search, result formatting,
    and verse saving for the keyword tab.
    """

    def __init__(self, settings, tr_func):
        """
        Initializes the logic handler with settings and translation function.

        :param settings: Global application settings
        :type settings: dict
        :param tr_func: Translation function
        :type tr_func: Callable[[str], str]
        """
        self.settings = settings
        self.tr = tr_func

    def run_search(self, parent):
        """
        Performs a keyword search and updates the result table and summary box.

        :param parent: The TabKeyword instance (UI context)
        :type parent: QWidget
        """
        log_debug("[TabKeyword] run_search started")
        version = parent.version_box.currentText()
        keywords = parent.keyword_input.text().strip().split()

        # Ensure keyword input is not empty
        if not keywords or all(k == "" for k in keywords):
            QMessageBox.warning(parent, parent.tr("warn_input_title"), parent.tr("warn_input_msg"))
            return

        # Determine search mode based on radio button selection
        mode = "compact" if parent.radio_compact.isChecked() else "and"

        # Execute search using the keyword search engine
        searcher = BibleKeywordSearcher(version)
        results = searcher.search(" ".join(keywords), mode=mode)  # pass mode explicitly
        counts = searcher.count_keywords(results, keywords)

        parent.update_table(results)
        parent.update_summary(counts)
        log_debug(f"[TabKeyword] search results: {len(results)} found")

        parent.summary_box.append("")  # add spacing line
        parent.summary_box.append(f"{parent.tr('total_results_label')} {len(results)}")

        if not results:
            QMessageBox.information(parent, parent.tr("info_no_results_title"), parent.tr("info_no_results_msg"))


    def save_selected_verse(self, parent):
        """
        Saves the currently selected verse in the result table to a file.

        :param parent: The TabKeyword instance
        :type parent: QWidget
        """
        log_debug("[TabKeyword] save_selected_verse called")
        row = parent.table.currentRow()
        if row >= 0:
            ref = parent.table.item(row, 0).text()
            book_str, chap_verse = ref.rsplit(' ', 1)
            book = resolve_book_name(book_str) or book_str
            chapter, verse = chap_verse.split(':')
            chapter = int(chapter)
            verse = int(verse)

            # Normalize book ID for dictionary lookup
            normalized = book.replace(" ", "")
            version = parent.version_box.currentText()
            verses = parent.bible_data.get_verses(version)

            book = normalized
            if book not in verses:
                for key in verses:
                    if key.lower().replace(" ", "") == book.lower().replace(" ", ""):
                        book = key
                        break
                else:
                    log_debug(f"[TabKeyword] Book '{book}' not found in version {version}")
                    QMessageBox.warning(parent, parent.tr("warn_no_chapter_title"),
                                        parent.tr("warn_no_chapter_msg").format(normalized, chapter))
                    return

            # Build formatted output using utility
            verse_range = (verse, verse)
            book_alias = parent.bible_data.get_book_alias(parent.current_language)
            version_alias = parent.bible_data.get_version_alias(parent.current_language)

            merged = format_output(
                [version],
                book,
                str(chapter),
                verse_range,
                {version: verses},
                parent.tr,
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
                QMessageBox.critical(
                    parent,
                    parent.tr("error_saving_title"),
                    parent.tr("error_saving_msg").format(e)
                )
        else:
            QMessageBox.warning(
                parent,
                parent.tr("warn_selection_title"),
                parent.tr("warn_selection_msg")
            )

    def clear_outputs(self, parent):
        """
        Clears all output files by writing an empty string.

        :param parent: TabKeyword instance
        :type parent: QWidget
        """
        save_to_files("", parent.settings)

    def update_table(self, parent, results):
        """
        Populates the result table with search results.

        :param parent: TabKeyword instance
        :type parent: QWidget
        :param results: List of verse entries with book/chapter/verse/text/highlighted
        :type results: list[dict]
        """
        parent.table.setRowCount(0)
        for i, res in enumerate(results):
            parent.table.insertRow(i)

            # Format reference (book + chapter:verse)
            display_book = parent.bible_data.get_standard_book(res['book'], parent.current_language)
            ref_item = QTableWidgetItem(f"{display_book} {res['chapter']}:{res['verse']}")
            ref_item.setFont(parent.table.font())
            ref_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            ref_item.setFlags(ref_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            parent.table.setItem(i, 0, ref_item)

            # Add verse content with highlight info as tooltip
            item = QTableWidgetItem(res['text'])
            item.setFont(parent.table.font())
            item.setToolTip(res['highlighted'])
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            parent.table.setItem(i, 1, item)

        parent.table.setWordWrap(True)
        parent.table.resizeRowsToContents()
    
        # Set padding for cleaner spacing
        parent.table.setStyleSheet("QTableWidget::item { padding: 6px; }")

        # Ensure content-based height + add breathing room
        parent.table.resizeRowsToContents()
        for row in range(parent.table.rowCount()):
            h = parent.table.rowHeight(row)
            parent.table.setRowHeight(row, h + 4)

    def update_summary(self, parent, counts):
        """
        Updates the keyword usage summary based on search results.

        :param parent: TabKeyword instance
        :type parent: QWidget
        :param counts: Dictionary of keyword -> count mappings
        :type counts: dict[str, int]
        """
        parent.summary_box.setPlainText("\n".join(f"{k}: {v}" for k, v in counts.items()))