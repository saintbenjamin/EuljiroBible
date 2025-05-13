# core/utils/verse_version_helper.py

from PySide6.QtWidgets import QCheckBox, QLayoutItem
from core.logic.verse_logic import (
    get_common_books_among_versions,
    validate_versions_and_books,
)


class VerseVersionHelper:
    """
    Provides logic for handling selected versions and common books
    based on the Bible dataset and version layout.
    """

    def __init__(self, bible_data, version_layout):
        """
        Args:
            bible_data: Instance of BibleDataLoader
            version_layout: Layout containing QCheckBox widgets for versions
        """
        self.bible_data = bible_data
        self.version_layout = version_layout

    def get_selected_versions(self):
        """
        Returns a list of selected version keys.

        Returns:
            list[str]: Selected Bible versions.
        """
        selected = []
        for i in range(self.version_layout.count()):
            item = self.version_layout.itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if isinstance(widget, QCheckBox):
                if widget.isChecked():
                    selected.append(widget.version_key)
        return selected

    def get_common_books(self):
        """
        Finds common books among selected versions.

        Returns:
            list[str]: Common book names.
        """
        versions = self.get_selected_versions()
        if not versions:
            return []

        common_books = get_common_books_among_versions(
            versions, self.bible_data.get_verses, self.bible_data
        )
        all_books = list(self.bible_data.standard_book.keys())
        return [b for b in all_books if b in common_books]

    def validate_selection(self, initializing=False):
        """
        Validates that versions and common books are available.

        Returns:
            tuple: (versions, common_books)
        """
        if initializing:
            return self.get_selected_versions(), self.get_common_books()

        versions = self.get_selected_versions()
        validated_versions, common_books = validate_versions_and_books(versions, self.bible_data)
        return validated_versions, common_books

    def sort_versions(self, version_list):
        """
        Sorts version names based on sort_order and book prefix.

        Args:
            version_list (list): Bible version keys.

        Returns:
            list: Sorted version list.
        """
        version_list.sort(key=self.bible_data.get_sort_key())

        def custom_sort_key(version):
            prefix = version.split()[0]
            return (self.bible_data.sort_order.get(prefix, 99), version)

        version_list.sort(key=custom_sort_key)
        return version_list