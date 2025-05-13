import platform

from PySide6.QtWidgets import QMessageBox, QCheckBox

from core.utils.bible_parser import resolve_book_name
from core.utils.logger import log_debug

from gui.ui.common import create_checkbox
from gui.utils.logger import log_error_with_dialog

class TabVerseSelectionManager:
    """
    Manages the logic for updating the book dropdown based on selected versions and language.
    """

    def __init__(self, bible_data, version_helper, tr_func):
        """
        Args:
            bible_data: BibleDataLoader instance
            version_helper: VersionHelper instance
            tr_func: Translation function
        """
        self.bible_data = bible_data
        self.version_helper = version_helper
        self.tr = tr_func

    def create_version_checkbox(self, parent, version_name):
        """
        Creates a version checkbox widget.

        Args:
            version_name (str): Full version name.

        Returns:
            QCheckBox: The version checkbox.
        """
        label = parent.bible_data.aliases_version.get(version_name, version_name)
        checkbox = create_checkbox(label, callback=lambda _: self.update_version_summary(parent))
        checkbox.version_key = version_name
        checkbox.setToolTip(version_name)
        checkbox.setEnabled(True)    

        return checkbox

    def update_grid_layout(self, parent):
        """
        Updates the layout grid dynamically based on width.
        """
        width = parent.version_scroll.viewport().width()

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
        Updates the selected version summary label and refreshes the book dropdown.
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
                QMessageBox.critical(self,
                    parent.tr("error_loading_title"),
                    parent.tr("error_loading_msg").format(v, e))

    def populate_book_dropdown(self, parent, lang_code=None):
        """
        Populates the book dropdown list based on language.

        Args:
            lang_code (str, optional): Language code.
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
        Updates the book dropdown to match selected versions.

        Args:
            parent: The TabVerse instance (contains UI references)
            lang_code (str): Language code to use ("ko" or "en")

        Handles:
            - No version selected → skip with no warning
            - No common books → clear + warning
            - Previously selected book no longer available → fallback + warning
            - Empty previous state → fallback with no warning
        """
        if getattr(parent, "initializing", False):
            return

        if lang_code is None:
            lang_code = "en" if self.tr("menu_lang") == "Language" else "ko"

        versions = self.version_helper.get_selected_versions()

        if not versions:
            parent.book_combo.blockSignals(True)
            parent.book_combo.clear()
            parent.book_combo.blockSignals(False)
            parent.chapter_input.clear()
            parent.verse_input.clear()
            return

        common_books = self.version_helper.get_common_books()
        versions, common_books = self.version_helper.validate_selection()

        if not common_books:
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

        current_display_text = parent.book_combo.currentText().strip()
        current_book_eng = resolve_book_name(current_display_text, lang_code)
        current_chapter = parent.chapter_input.currentText().strip()
        current_verse = parent.verse_input.text().strip()

        parent.book_combo.blockSignals(True)
        parent.book_combo.clear()

        for book in common_books:
            display_name = self.bible_data.get_standard_book(book, lang_code)
            parent.book_combo.addItem(display_name, userData=book)

        parent.book_combo.blockSignals(False)

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

        self.update_chapter_dropdown(parent)
        parent.chapter_input.setCurrentText(current_chapter)
        parent.verse_input.setText(current_verse)

    def update_chapter_dropdown(self, parent):
        """
        Updates the chapter dropdown based on selected book and version.
        """
        selected_versions = parent.version_helper.get_selected_versions()
        if not selected_versions:
            return

        version = selected_versions[0]
        book_display = parent.book_combo.currentText().strip()
        book = resolve_book_name(book_display, parent.bible_data, parent.current_language)
    
        if not book:
            parent.chapter_input.clear()
            return
    
        if book in parent.bible_data.get_verses(version):
            chapters = parent.bible_data.get_verses(version).get(book, {}).keys()
            max_chapter = max(int(ch) for ch in chapters)
            parent.chapter_input.blockSignals(True)
            parent.chapter_input.clear()
            parent.chapter_input.addItems([str(i) for i in range(1, max_chapter + 1)])
            parent.chapter_input.setEditText("")
            parent.chapter_input.blockSignals(False)
        else:
            parent.chapter_input.clear()