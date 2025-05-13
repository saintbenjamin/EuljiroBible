# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/verse_version_helper.py
Performs logic for managing selected Bible versions and computing shared books.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtWidgets import QCheckBox, QLayoutItem
from core.logic.verse_logic import (
    get_common_books_among_versions,
    validate_versions_and_books,
)

class VerseVersionHelper:
    """
    Handles logic related to selected Bible versions and finding common books.

    :param bible_data: Bible data loader instance
    :type bible_data: BibleDataLoader
    :param version_layout: Layout containing QCheckBox widgets for each version
    :type version_layout: QLayout
    """

    def __init__(self, bible_data, version_layout):
        """
        Initialize the helper with data source and layout.

        :param bible_data: Instance of BibleDataLoader
        :type bible_data: BibleDataLoader
        :param version_layout: Layout containing QCheckBox widgets
        :type version_layout: QLayout
        """
        self.bible_data = bible_data
        self.version_layout = version_layout

    def get_selected_versions(self):
        """
        Returns a list of selected Bible versions based on checked checkboxes.

        :return: List of selected version keys
        :rtype: list[str]
        """
        selected = []
        for i in range(self.version_layout.count()):
            item = self.version_layout.itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if isinstance(widget, QCheckBox):
                if widget.isChecked():
                    # Add the version key if the checkbox is checked
                    selected.append(widget.version_key)
        return selected

    def get_common_books(self):
        """
        Find common books among all selected Bible versions.

        :return: List of book names common to all selected versions
        :rtype: list[str]
        """
        versions = self.get_selected_versions()
        if not versions:
            return []

        # Use helper logic to find common books across versions
        common_books = get_common_books_among_versions(
            versions, self.bible_data.get_verses, self.bible_data
        )

        # Only keep books that are recognized in the standard book list
        all_books = list(self.bible_data.standard_book.keys())
        return [b for b in all_books if b in common_books]

    def validate_selection(self, initializing=False):
        """
        Validates selected versions and retrieves common books.

        :param initializing: If True, skip validation logic
        :type initializing: bool
        :return: Tuple of (validated versions, common books)
        :rtype: tuple[list[str], list[str]]
        """
        if initializing:
            return self.get_selected_versions(), self.get_common_books()

        # Validate selected versions and compute shared books
        versions = self.get_selected_versions()
        validated_versions, common_books = validate_versions_and_books(versions, self.bible_data)
        return validated_versions, common_books

    def sort_versions(self, version_list):
        """
        Sort the version list by internal sort order and prefix rules.

        :param version_list: List of version keys to sort
        :type version_list: list[str]
        :return: Sorted list of version keys
        :rtype: list[str]
        """
        # Sort by the global sort key first
        version_list.sort(key=self.bible_data.get_sort_key())

        def custom_sort_key(version):
            prefix = version.split()[0]
            # Apply secondary sorting based on prefix ordering
            return (self.bible_data.sort_order.get(prefix, 99), version)

        version_list.sort(key=custom_sort_key)
        return version_list