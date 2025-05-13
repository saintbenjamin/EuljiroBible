# -*- coding: utf-8 -*-
"""
File: tab_keyword_logic.py
Handles the keyword search, result display, and saving logic for TabKeyword.
"""


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem, QMessageBox

from core.utils.bible_keyword_searcher import BibleKeywordSearcher
from core.utils.bible_parser import resolve_book_name
from core.utils.logger import log_debug
from core.utils.utils_output import format_output, save_to_files

class TabKeywordLogic:
    """
    Logic handler for keyword-based Bible search and result operations.
    """

    def __init__(self, settings, tr_func):
        self.settings = settings
        self.tr = tr_func

    def run_search(self, parent):
        """
        Executes a keyword search in the selected version.
        Populates table and summary with results.
        """
        log_debug("[TabKeyword] run_search started")
        version = parent.version_box.currentText()
        keywords = parent.keyword_input.text().strip().split()

        # Validate keyword input
        if not keywords or all(k == "" for k in keywords):
            QMessageBox.warning(
                parent, 
                parent.tr("warn_input_title"), 
                parent.tr("warn_input_msg"))
            return

        # Perform search and generate summary
        searcher = BibleKeywordSearcher(version)
        results = searcher.search(" ".join(keywords))
        counts = searcher.count_keywords(results, keywords)

        parent.update_table(results)
        parent.update_summary(counts)
        log_debug(f"[TabKeyword] search results: {len(results)} found")

        # Add count to summary box
        parent.summary_box.append("")  # spacing
        parent.summary_box.append(f"{parent.tr('total_results_label')} {len(results)}")

        if not results:
            QMessageBox.information(
                parent, 
                parent.tr("info_no_results_title"), 
                parent.tr("info_no_results_msg"))


    def save_selected_verse(self, parent):
        """
        Saves the currently selected verse from search results.
        """
        log_debug("[TabKeyword] save_selected_verse called")
        row = parent.table.currentRow()
        if row >= 0:
            ref = parent.table.item(row, 0).text()

            # Extract book, chapter, and verse from selected reference
            book_str, chap_verse = ref.rsplit(' ', 1)
            book = resolve_book_name(book_str) or book_str  # fallback for safety
            chapter, verse = chap_verse.split(':')
            chapter = int(chapter)
            verse = int(verse) 

            normalized = book.replace(" ", "")
            version = parent.version_box.currentText()
            verses = parent.bible_data.get_verses(version)

            # Resolve canonical book name
            book = normalized
            if book not in verses:
                for key in verses:
                    if key.lower().replace(" ", "") == book.lower().replace(" ", ""):
                        book = key
                        break
                else:
                    log_debug(f"[TabKeyword] Book '{book}' not found in version {version}")
                    QMessageBox.warning(parent, parent.tr("warn_no_chapter_title"), parent.tr("warn_no_chapter_msg").format(normalized, chapter))
                    return

            # Create output and save
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
            # No row selected
            QMessageBox.warning(
                parent,
                parent.tr("warn_selection_title"),
                parent.tr("warn_selection_msg")
            )

    def clear_outputs(self, parent):
        """
        Clears output files.
        """
        save_to_files("", parent.settings)        

    def update_table(self, parent, results):
        """
        Updates the search results table with found verses.

        Args:
            results (list): List of search result entries.
        """
        parent.table.setRowCount(0)
        for i, res in enumerate(results):
            parent.table.insertRow(i)

            display_book = parent.bible_data.get_standard_book(res['book'], parent.current_language)
            ref_item = QTableWidgetItem(f"{display_book} {res['chapter']}:{res['verse']}")
            ref_item.setFont(parent.table.font())
            ref_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            ref_item.setFlags(ref_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            parent.table.setItem(i, 0, ref_item)

            item = QTableWidgetItem(res['text'])
            item.setFont(parent.table.font())
            item.setToolTip(res['highlighted'])
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            parent.table.setItem(i, 1, item)

        parent.table.setWordWrap(True)
        parent.table.resizeRowsToContents()

    def update_summary(self, parent, counts):
        """
        Updates the keyword counts summary box.

        Args:
            counts (dict): Dictionary mapping keywords to their counts.
        """
        parent.summary_box.setPlainText("\n".join(f"{k}: {v}" for k, v in counts.items()))
