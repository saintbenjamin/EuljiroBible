# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_verse_selection_manager.py
Handles version selection and book/chapter dropdown synchronization in the TabVerse panel.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import platform
from PySide6.QtWidgets import QMessageBox, QCheckBox

from core.utils.bible_parser import resolve_book_name
from core.utils.logger import log_debug
from gui.ui.common import create_checkbox
from gui.utils.logger import log_error_with_dialog


class TabVerseSelectionManager:
    """
    Manages the logic for updating version checkboxes, summary label,
    and dropdowns for book and chapter selection in the TabVerse UI.

    :param bible_data: Instance of BibleDataLoader
    :type bible_data: BibleDataLoader
    :param version_helper: Helper for version selection and validation
    :type version_helper: VerseVersionHelper
    :param tr_func: Translation function (usually `self.tr`)
    :type tr_func: Callable[[str], str]
    """

    def __init__(self, bible_data, version_helper, tr_func):
        """
        Initialize the manager with data and helpers.

        :param bible_data: Bible data loader
        :param version_helper: Instance for managing selected versions
        :param tr_func: Translation function
        """
        self.bible_data = bible_data
        self.version_helper = version_helper
        self.tr = tr_func

    def create_version_checkbox(self, parent, version_name):
        """
        Creates a checkbox for a given Bible version.

        :param parent: Parent widget with access to bible_data and update method
        :param version_name: Full name of the version
        :type version_name: str
        :return: Configured QCheckBox
        :rtype: QCheckBox
        """
        label = parent.bible_data.aliases_version.get(version_name, version_name)
        checkbox = create_checkbox(label, callback=lambda _: self.update_version_summary(parent))
        checkbox.version_key = version_name
        checkbox.setToolTip(version_name)
        checkbox.setEnabled(True)
        return checkbox

    def update_grid_layout(self, parent):
        """
        Updates the layout grid for version checkboxes based on platform-specific width.

        :param parent: Parent widget with scroll and layout references
        """
        width = parent.version_scroll.viewport().width()

        # Use different ratios for Windows vs others due to scrollbar/rendering differences
        if platform.system() == "Windows":
            column_width = 190
            usable_width = int(width * 0.6)
        else:
            column_width = 170
            usable_width = int(width * 0.7)

        columns = max(1, usable_width // column_width)

        for idx, checkbox in enumerate(parent.version_widget.findChildren(QCheckBox)):
            parent.version_layout.addWidget(checkbox, idx // columns, idx % columns)

    def update_version_summary(self, parent):
        """
        Updates the label summarizing selected versions and repopulates book dropdown.

        :param parent: TabVerse instance with summary label and dropdown widgets
        """
        if getattr(parent, "initializing", False):
            return

        selected_versions = parent.version_helper.get_selected_versions()

        if selected_versions:
            if parent.use_alias:
                summary = ", ".join([parent.bible_data.aliases_version.get(v, v) for v in selected_versions])
            else:
                summary = ", ".join(selected_versions)
        else:
            summary = parent.tr("msg_nothing")
            QMessageBox.warning(
                parent,
                parent.tr("warn_version_title"),
                parent.tr("warn_version_msg")
            )
            parent.book_combo.clear()
            parent.chapter_input.clear()
            parent.verse_input.clear()
            return

        parent.version_summary_label.setText(summary)
        self.update_book_dropdown(parent, parent.current_language)

        for v in selected_versions:
            try:
                log_debug(f"[TabVerse] selected versions: {parent.version_helper.get_selected_versions()}")
            except Exception as e:
                log_error_with_dialog(e)
                QMessageBox.critical(
                    parent,
                    parent.tr("error_loading_title"),
                    parent.tr("error_loading_msg").format(v, e)
                )

    def populate_book_dropdown(self, parent, lang_code=None):
        """
        Populates the book dropdown with all standard books.

        :param parent: TabVerse instance with combo box
        :param lang_code: Language code ('ko' or 'en')
        :type lang_code: str | None
        """
        if lang_code is None:
            lang_code = "ko"

        parent.book_combo.blockSignals(True)
        parent.book_combo.clear()

        for book_key, names in parent.bible_data.standard_book.items():
            display_name = names.get(lang_code, book_key)
            parent.book_combo.addItem(display_name)

        parent.book_combo.setCurrentIndex(0)
        parent.book_combo.blockSignals(False)

    def update_book_dropdown(self, parent, lang_code=None):
        """
        Updates the book dropdown to show only those available in all selected versions.

        :param parent: TabVerse instance with input fields and book combo box
        :param lang_code: Language code ('ko' or 'en')
        """
        if getattr(parent, "initializing", False):
            return

        if lang_code is None:
            lang_code = "en" if self.tr("menu_lang") == "Language" else "ko"

        versions = self.version_helper.get_selected_versions()

        if not versions:
            # Clear all inputs if no versions are selected
            parent.book_combo.blockSignals(True)
            parent.book_combo.clear()
            parent.book_combo.blockSignals(False)
            parent.chapter_input.clear()
            parent.verse_input.clear()
            return

        # Validate and get common books
        common_books = self.version_helper.get_common_books()
        versions, common_books = self.version_helper.validate_selection()

        if not common_books:
            # Warn user if no books are shared among selected versions
            parent.book_combo.blockSignals(True)
            parent.book_combo.clear()
            parent.book_combo.blockSignals(False)
            parent.chapter_input.clear()
            parent.verse_input.clear()
            QMessageBox.warning(
                parent,
                self.tr("warn_common_book_title"),
                self.tr("warn_common_book_msg")
            )
            return

        # Backup current selections
        current_display_text = parent.book_combo.currentText().strip()
        current_book_eng = resolve_book_name(current_display_text, lang_code)
        current_chapter = parent.chapter_input.currentText().strip()
        current_verse = parent.verse_input.text().strip()

        # Update the book dropdown list
        parent.book_combo.blockSignals(True)
        parent.book_combo.clear()
        for book in common_books:
            display_name = self.bible_data.get_standard_book(book, lang_code)
            parent.book_combo.addItem(display_name, userData=book)
        parent.book_combo.blockSignals(False)

        # Try to restore previous selection
        found = False
        for i in range(parent.book_combo.count()):
            if parent.book_combo.itemData(i) == current_book_eng:
                parent.book_combo.setCurrentIndex(i)
                found = True
                break

        if not found:
            parent.book_combo.setCurrentIndex(0)
            if current_display_text:
                QMessageBox.warning(
                    parent,
                    self.tr("warn_common_book_title"),
                    self.tr("warn_book_not_in_versions_msg")
                )

        # Reapply previous chapter/verse values
        self.update_chapter_dropdown(parent)
        parent.chapter_input.setCurrentText(current_chapter)
        parent.verse_input.setText(current_verse)

    def update_chapter_dropdown(self, parent):
        """
        Updates the chapter dropdown to reflect the selected book and version.

        :param parent: TabVerse instance with combo boxes and data access
        """
        selected_versions = parent.version_helper.get_selected_versions()
        if not selected_versions:
            return

        version = selected_versions[0]
        book_display = parent.book_combo.currentText().strip()

        # Resolve internal book name
        book = resolve_book_name(book_display, parent.bible_data, parent.current_language)

        if not book:
            parent.chapter_input.clear()
            return

        if book in parent.bible_data.get_verses(version):
            # Get chapter numbers from the version's verse structure
            chapters = parent.bible_data.get_verses(version).get(book, {}).keys()
            max_chapter = max(int(ch) for ch in chapters)

            parent.chapter_input.blockSignals(True)
            parent.chapter_input.clear()
            parent.chapter_input.addItems([str(i) for i in range(1, max_chapter + 1)])
            parent.chapter_input.setEditText("")
            parent.chapter_input.blockSignals(False)
        else:
            parent.chapter_input.clear()