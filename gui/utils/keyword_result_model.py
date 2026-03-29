# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/keyword_result_model.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Provides a QAbstractTableModel for displaying Bible keyword search results.
"""

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex

class KeywordResultTableModel(QAbstractTableModel):
    """
    Table model for displaying Bible keyword search results.

    This QAbstractTableModel exposes a fixed 3-column table:
        0) Row index number (1-based)
        1) Localized reference string: "<Book> <chapter>:<verse>"
        2) Verse text

    Attributes:
        results (List[dict]): List of search result entries. Each entry is expected to
            contain at least: "book", "chapter", "verse", and "text".
        bible_data (BibleDataLoader): Data loader used to resolve localized/standard
            book display names.
        language (str): Active language code used for localization (e.g., "ko", "en").
        tr (Callable[[str], str]): Translation function for header labels and UI text.
    """

    def __init__(self, results, bible_data, current_language, tr):
        """
        Initialize the model with results and localization helpers.

        Args:
            results (List[dict] | None): Search results to display. If None, an empty list is used.
            bible_data (BibleDataLoader): Bible data loader used for book-name localization.
            current_language (str): Language code for localized book names (e.g., "ko", "en").
            tr (Callable[[str], str]): Translation function for localized header strings.
        """
        super().__init__()
        self.results = results or []
        self.bible_data = bible_data
        self.language = current_language
        self.tr = tr 

    def rowCount(self, parent=QModelIndex()):
        """
        Return the number of rows in the table.

        Args:
            parent (QModelIndex): Unused Qt parent index.

        Returns:
            int: Number of result rows.
        """
        return len(self.results)

    def columnCount(self, parent=QModelIndex()):
        """
        Return the number of columns in the table.

        The model always returns 3 columns:
            0 - Row index number
            1 - Reference (localized book + chapter:verse)
            2 - Verse text

        Args:
            parent (QModelIndex): Unused Qt parent index.

        Returns:
            int: Always 3.
        """
        return 3

    def data(self, index, role=Qt.DisplayRole):
        """
        Return cell data for the given index and role.

        Only Qt.DisplayRole is handled. Other roles return None.

        Args:
            index (QModelIndex): Model index indicating the target cell.
            role (int): Qt item data role.

        Returns:
            str | None: Display string for the cell, or None if not applicable.
        """
        if not index.isValid():
            return None

        res = self.results[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return str(index.row() + 1)  # Row number
            elif index.column() == 1:
                # Localized book name + chapter:verse
                display_book = self.bible_data.get_standard_book(res['book'], self.language)
                return f"{display_book} {res['chapter']}:{res['verse']}"
            elif index.column() == 2:
                return res['text']  # Verse text

        return None

    def headerData(self, section, orientation, role):
        """
        Return header labels for the table.

        Only Qt.DisplayRole with Qt.Horizontal orientation is handled.

        Args:
            section (int): Column index.
            orientation (Qt.Orientation): Header orientation.
            role (int): Qt item data role.

        Returns:
            str | None: Header label for the given column, or None if not applicable.
        """
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["", self.tr("search_location"), self.tr("search_verse")][section]
        return None