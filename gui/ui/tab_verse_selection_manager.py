# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/ui/tab_verse_selection_manager.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Handles version selection and book/chapter dropdown synchronization in the TabVerse panel.
"""

import platform
from PySide6.QtWidgets import QMessageBox, QCheckBox

from core.utils.bible_parser import resolve_book_name
from core.utils.logger import log_debug
from gui.ui.common import create_checkbox
from gui.utils.logger import log_error_with_dialog

class TabVerseSelectionManager:
    """
    Selection and dropdown manager for the TabVerse UI.

    This class manages version checkbox layout and selection state, the version
    summary label, and the book/chapter dropdown behavior for the verse tab. It
    coordinates with VerseVersionHelper to validate version selections and compute
    the set of common books available across selected versions.

    Attributes:
        bible_data (BibleDataLoader): Bible data loader instance used to resolve
            standard book names and verse structures.
        version_helper (VerseVersionHelper): Helper used to read selected versions,
            validate selections, and compute common books.
        tr (Callable[[str], str]): Translation function used for localized UI messages.
    """

    def __init__(self, bible_data, version_helper, tr_func):
        """
        Initialize the selection manager with Bible data and helper dependencies.

        Args:
            bible_data (BibleDataLoader): Bible data loader instance.
            version_helper (VerseVersionHelper): Helper used to manage selected versions.
            tr_func (Callable[[str], str]): Translation function for localized UI strings.
        """
        self.bible_data = bible_data
        self.version_helper = version_helper
        self.tr = tr_func

    def create_version_checkbox(self, parent, version_name):
        """
        Create a version selection checkbox for a given Bible version.

        The checkbox label uses the GUI alias mapping when available, while the
        underlying version key is stored on the widget as `version_key`.

        Args:
            parent (QWidget): Parent UI instance used to access bible_data and update callbacks.
            version_name (str): Full version identifier.

        Returns:
            QCheckBox: Configured checkbox instance.
        """
        label = parent.bible_data.aliases_version.get(version_name, version_name)
        checkbox = create_checkbox(label, callback=lambda _: self.update_version_summary(parent))
        checkbox.version_key = version_name
        checkbox.setToolTip(version_name)
        checkbox.setEnabled(True)
        return checkbox

    def update_grid_layout(self, parent):
        """
        Reflow the version checkbox grid layout based on the current viewport width.

        This recomputes the number of columns from the available width and places
        checkboxes into the grid accordingly. Platform-specific width ratios are used
        to account for rendering/scrollbar differences.

        Args:
            parent (QWidget): TabVerse instance containing the version scroll area and grid layout.
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
        Update the selected-version summary label and refresh dependent dropdowns.

        If no versions are selected, this clears book/chapter/verse inputs and shows a
        warning dialog. Otherwise, it updates the summary label (alias vs full name)
        and refreshes the book dropdown to reflect books common to all selected versions.

        Args:
            parent (QWidget): TabVerse instance containing summary label and dropdown widgets.
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
        Populate the book dropdown with the full standard book list.

        This is used to initialize the book dropdown independent of version filtering.

        Args:
            parent (QWidget): TabVerse instance containing the book combo box.
            lang_code (str | None): Language code used for display names (default: "ko").
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
        Update the book dropdown to include only books common to all selected versions.

        This validates the selected versions, computes the intersection of supported
        books, updates the dropdown entries accordingly, and attempts to restore any
        previous book/chapter/verse selections when possible.

        Args:
            parent (QWidget): TabVerse instance containing book/chapter/verse input widgets.
            lang_code (str | None): Language code used for display names. If not provided,
                it is inferred from the current translation context.
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
        Update the chapter dropdown for the currently selected book.

        This resolves the internal book key, reads available chapter indices from the
        selected version's verse structure, and fills the chapter combo box with a
        1..max range.

        Args:
            parent (QWidget): TabVerse instance containing the book and chapter widgets.
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