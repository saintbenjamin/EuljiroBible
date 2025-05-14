# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/keyword_result_model.py
Provides a QAbstractTableModel for displaying Bible keyword search results.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex

class KeywordResultTableModel(QAbstractTableModel):
    """
    QAbstractTableModel implementation for Bible keyword search results.

    This model provides three columns:
    0. Row number
    1. Book + chapter:verse (with localized alias)
    2. Verse text

    :param results: List of verse dictionaries
    :param bible_data: BibleDataLoader instance for resolving book aliases
    :param current_language: Language code (e.g., 'ko', 'en') for localization
    :param tr: Translation function
    """

    def __init__(self, results, bible_data, current_language, tr):
        super().__init__()
        self.results = results or []
        self.bible_data = bible_data
        self.language = current_language
        self.tr = tr 

    def rowCount(self, parent=QModelIndex()):
        """
        Returns the number of rows in the model.

        :param parent: QModelIndex (not used)
        :return: Row count
        """
        return len(self.results)

    def columnCount(self, parent=QModelIndex()):
        """
        Returns the number of columns in the model.

        Columns:
        0 - Index number
        1 - Reference (book + chapter:verse)
        2 - Verse text

        :param parent: QModelIndex (not used)
        :return: Column count (always 3)
        """
        return 3

    def data(self, index, role=Qt.DisplayRole):
        """
        Returns the data for a given cell in the model.

        :param index: QModelIndex specifying row and column
        :param role: Qt item role (only DisplayRole is handled)
        :return: Display string for the given index
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
        Returns the header labels for columns.

        :param section: Column index
        :param orientation: Qt.Horizontal or Qt.Vertical
        :param role: Qt item role
        :return: Header label string or None
        """
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["", self.tr("search_location"), self.tr("search_verse")][section]
        return None