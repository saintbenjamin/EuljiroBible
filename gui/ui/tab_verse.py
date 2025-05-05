# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/ui/tab_verse.py
Description: Implements the TabVerse for EuljiroBible, allowing Bible verse lookup, navigation, display, and output.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import platform

from PySide6.QtCore import Qt
from PySide6.QtWidgets import ( 
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QComboBox, QTextEdit, QMessageBox, QScrollArea, QGridLayout, QCheckBox, 
    QSplitter, QApplication
)
from PySide6.QtGui import QTextBlockFormat, QStandardItemModel, QFont

from core.logic.verse_logic import display_verse_logic
from core.store.storage import loaded_versions
from core.utils.bible_data_loader import BibleDataLoader
from core.utils.logger import log_debug
from core.utils.utils_bible import get_max_verse, resolve_book_name, compact_book_id
from core.utils.utils_output import save_to_files
from gui.ui.common import create_checkbox, create_svg_text_button, LoadingIndicator
from gui.ui.locale.message_loader import load_messages
from gui.utils.logger import log_error_with_dialog
from gui.utils.utils_window import find_window_main

class TabVerse(QWidget):
    """
    Tab for looking up, displaying, navigating, and saving Bible verses.

    Allows selecting versions, inputting book/chapter/verse, viewing results, and exporting them.
    """

    def __init__(self, version_list, settings, tr):
        """
        Initializes the TabVerse.

        Args:
            version_list (list): List of available Bible versions.
            settings (dict): Loaded user settings.
            tr (function): Translation function.
        """
        super().__init__()
        self.tr = tr
        self.initializing = False
        self.settings = settings
        self.formatted_verse_text = ""

        self.bible_data = BibleDataLoader()
        self.version_list = self.sort_versions(version_list)
        self.init_ui()

    def init_ui(self):
        self.version_scroll = QScrollArea()
        self.version_scroll.setWidgetResizable(True)
        self.version_widget = QWidget()
        self.version_layout = QGridLayout(self.version_widget)
        self.version_scroll.setWidget(self.version_widget)

        for version in enumerate(self.version_list):
            if isinstance(version, tuple):
                _, version_name = version
            else:
                version_name = version

            checkbox = self.create_version_checkbox(version_name)
            self.version_layout.addWidget(checkbox)

        self.update_grid_layout()

        self.enter_state = 0
        self.use_alias = False

        self.alias_toggle_btn = QPushButton(self.tr("label_alias_full"))
        self.alias_toggle_btn.setCheckable(True)
        self.alias_toggle_btn.setChecked(False)
        self.alias_toggle_btn.clicked.connect(self.toggle_alias_mode)

        self.version_summary_label = QLabel(self.tr("msg_nothing"))
        version_label_layout = QHBoxLayout()
        version_label_layout.addWidget(self.alias_toggle_btn)
        version_label_layout.addWidget(self.version_summary_label)
        version_label_layout.addStretch()

        self.book_label = QLabel(self.tr("label_book"))
        self.chapter_label = QLabel(self.tr("label_chapter"))
        self.verse_label = QLabel(self.tr("label_verse"))

        self.book_combo = QComboBox()
        self.book_combo.setModel(QStandardItemModel(self.book_combo))
        self.book_combo.setEditable(True)
        self.book_combo.setInsertPolicy(QComboBox.NoInsert)
        self.book_combo.currentTextChanged.connect(self.update_chapter_dropdown)

        self.chapter_input = QComboBox()
        self.chapter_input.setEditable(True)

        self.verse_input = QLineEdit()
        self.verse_input.setPlaceholderText(self.tr("verse_input_hint"))
        self.verse_input.returnPressed.connect(self.handle_enter)

        self.search_btn = create_svg_text_button(
            "resources/svg/btn_search.svg",
            self.tr("btn_search"),
            30,
            "Search",
            self.display_verse
        )
        self.save_btn = create_svg_text_button(
            "resources/svg/btn_output.svg",
            self.tr("btn_output"),
            30,
            "Start slide show",
            self.save_verse
        )
        self.clear_display_btn = create_svg_text_button(
            "resources/svg/btn_clear.svg",
            self.tr("btn_clear"),
            30,
            "Stop slide show",
            self.clear_outputs
        )
        self.prev_verse_btn = create_svg_text_button(
            "resources/svg/btn_prev.svg",
            self.tr("btn_prev"),
            30,
            "Go to previous verse",
            lambda: self.shift_verse(-1)
        )
        self.next_verse_btn = create_svg_text_button(
            "resources/svg/btn_next.svg",
            self.tr("btn_next"),
            30,
            "Go to next verse",
            lambda: self.shift_verse(1)
        )

        input_layout = QHBoxLayout()
        self.input_layout = input_layout
        input_layout.addWidget(self.book_label)
        input_layout.addWidget(self.book_combo)
        input_layout.addWidget(self.chapter_label)
        input_layout.addWidget(self.chapter_input)
        input_layout.addWidget(self.verse_label)
        input_layout.addWidget(self.verse_input)

        input_layout.setStretch(1, 2)
        input_layout.setStretch(3, 1)
        input_layout.setStretch(5, 1)

        button_layout = QHBoxLayout()
        self.button_layout = button_layout
        button_layout.addWidget(self.prev_verse_btn)
        button_layout.addWidget(self.search_btn)
        poll_enabled = self.settings.get("poll_enabled", False)
        if poll_enabled:
            button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.next_verse_btn)
        if poll_enabled:
            button_layout.addWidget(self.clear_display_btn)

        input_layout.addLayout(button_layout)

        self.display_box = QTextEdit()
        self.display_box.setReadOnly(True)

        self.loading_indicator = LoadingIndicator(self.display_box.viewport())
        self.loading_indicator.hide()

        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.addLayout(input_layout)
        bottom_layout.addWidget(self.display_box)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.version_scroll)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([150, 400]) 

        layout = QVBoxLayout()
        layout.addLayout(version_label_layout)
        layout.addWidget(splitter)

        self.setLayout(layout)
        layout.addWidget(self.loading_indicator) 

    def sort_versions(self, version_list):
        version_list.sort(key=self.bible_data.get_sort_key())

        def custom_sort_key(version):
            prefix = version.split()[0]
            return (self.bible_data.sort_order.get(prefix, 99), version)

        version_list.sort(key=custom_sort_key)
        return version_list

    def change_language(self, lang_code):
        """
        Changes the UI language dynamically.

        Args:
            lang_code (str): Language code.
        """
        self.current_language = lang_code
        self.messages = load_messages(lang_code)

        selected_versions = self.get_selected_versions()

        if selected_versions:
            if self.use_alias:
                summary = ", ".join([self.bible_data.aliases_version.get(v, v) for v in selected_versions])
            else:
                summary = ", ".join(selected_versions)
        else:
            summary = self.tr("msg_nothing")

        self.version_summary_label.setText(summary)

        self.book_label.setText(self.tr("label_book"))
        self.chapter_label.setText(self.tr("label_chapter"))
        self.verse_label.setText(self.tr("label_verse"))

        self.verse_input.setPlaceholderText(self.tr("verse_input_hint"))

        self.populate_book_dropdown(lang_code)

        if hasattr(self, "alias_toggle_btn"):
            if self.use_alias:
                self.alias_toggle_btn.setText(self.tr("label_alias_short"))
            else:
                self.alias_toggle_btn.setText(self.tr("label_alias_full"))

        self.update_book_dropdown(lang_code=lang_code)

        self.prev_verse_btn.setText(self.tr("btn_prev"))
        self.search_btn.setText(self.tr("btn_search"))
        self.save_btn.setText(self.tr("btn_output"))
        self.next_verse_btn.setText(self.tr("btn_next"))
        self.clear_display_btn.setText(self.tr("btn_clear"))

    def populate_book_dropdown(self, lang_code=None):
        """
        Populates the book dropdown list based on language.

        Args:
            lang_code (str, optional): Language code.
        """
        if lang_code is None:
            lang_code = "ko"

        self.book_combo.blockSignals(True)
        self.book_combo.clear()

        for book_key, names in self.bible_data.standard_book.items():
            display_name = names.get(lang_code, book_key)
            self.book_combo.addItem(display_name)

        self.book_combo.setCurrentIndex(0)
        self.book_combo.blockSignals(False)

    def update_book_dropdown(self, lang_code=None):
        """
        Updates the book dropdown to match selected versions.
        Handles:
        - No version selected → skip with no warning
        - No common books → clear + warning
        - Previously selected book no longer available → fallback + warning
        - Empty previous state → fallback with no warning
        """
        if getattr(self, "initializing", False):
            return

        if lang_code is None:
            lang_code = "en" if self.tr("menu_lang") == "Language" else "ko"

        versions = self.get_selected_versions()

        # ✅ Case 1: No versions selected at all — silent clear
        if not versions:
            self.book_combo.blockSignals(True)
            self.book_combo.clear()
            self.book_combo.blockSignals(False)
            self.chapter_input.clear()
            self.verse_input.clear()
            return

        common_books = self.get_common_books()
        versions, common_books = self.validate_selection()

        # ✅ Case 2: Versions selected but no common books
        if not common_books:
            self.book_combo.blockSignals(True)
            self.book_combo.clear()
            self.book_combo.blockSignals(False)
            self.chapter_input.clear()
            self.verse_input.clear()
            QMessageBox.warning(
                self,
                self.tr("warn_common_book_title"),
                self.tr("warn_common_book_msg")
            )
            return

        # ✅ Preserve current input before clearing UI
        current_display_text = self.book_combo.currentText().strip()
        current_book_eng = resolve_book_name(current_display_text, self.bible_data, lang_code)
        current_chapter = self.chapter_input.currentText().strip()
        current_verse = self.verse_input.text().strip()

        self.book_combo.blockSignals(True)
        self.book_combo.clear()

        for book in common_books:
            display_name = self.bible_data.get_standard_book(book, lang_code)
            self.book_combo.addItem(display_name, userData=book)

        self.book_combo.blockSignals(False)

        # ✅ Case 3: Restore previously selected book if still valid
        found = False
        for i in range(self.book_combo.count()):
            if self.book_combo.itemData(i) == current_book_eng:
                self.book_combo.setCurrentIndex(i)
                found = True
                break

        # ✅ Case 4: Not found → fallback + warning only if previously set
        if not found:
            self.book_combo.setCurrentIndex(0)
            if current_display_text:
                QMessageBox.warning(
                    self,
                    self.tr("warn_common_book_title"),
                    self.tr("warn_book_not_in_versions_msg")
                )

        # ✅ Restore chapter/verse input
        self.update_chapter_dropdown()
        self.chapter_input.setCurrentText(current_chapter)
        self.verse_input.setText(current_verse)


    def update_chapter_dropdown(self):
        """
        Updates the chapter dropdown based on selected book and version.
        """
        selected_versions = self.get_selected_versions()
        if not selected_versions:
            return

        version = selected_versions[0]
        book_display = self.book_combo.currentText().strip()
        book = resolve_book_name(book_display, self.bible_data, self.current_language)
    
        if not book:
            self.chapter_input.clear()
            return
    
        if book in self.bible_data.get_verses(version):
            chapters = self.bible_data.get_verses(version).get(book, {}).keys()
            max_chapter = max(int(ch) for ch in chapters)
            self.chapter_input.blockSignals(True)
            self.chapter_input.clear()
            self.chapter_input.addItems([str(i) for i in range(1, max_chapter + 1)])
            self.chapter_input.setEditText("")
            self.chapter_input.blockSignals(False)
        else:
            self.chapter_input.clear()

    def resizeEvent(self, event):
        """
        Handles window resize to adjust grid layout.

        Args:
            event (QResizeEvent): Resize event.
        """
        super().resizeEvent(event)
        self.update_grid_layout()

    def create_version_checkbox(self, version_name):
        """
        Creates a version checkbox widget.

        Args:
            version_name (str): Full version name.

        Returns:
            QCheckBox: The version checkbox.
        """
        label = self.bible_data.aliases_version.get(version_name, version_name)
        checkbox = create_checkbox(label, callback=self.update_version_summary)
        checkbox.version_key = version_name
        checkbox.setToolTip(version_name)
        checkbox.setEnabled(True)    

        return checkbox

    def update_grid_layout(self):
        """
        Updates the layout grid dynamically based on width.
        """
        width = self.version_scroll.viewport().width()

        if platform.system() == "Windows":
            column_width = 190
            usable_width = int(width * 0.6)        
        else:
            column_width = 170
            usable_width = int(width * 0.7)

        columns = max(1, usable_width // column_width)

        for idx, checkbox in enumerate(self.version_widget.findChildren(QCheckBox)):
            self.version_layout.addWidget(checkbox, idx // columns, idx % columns)

    def update_version_summary(self):
        """
        Updates the selected version summary label and refreshes the book dropdown.
        """
        if getattr(self, "initializing", False):
            return

        selected_versions = self.get_selected_versions()

        if selected_versions:
            if self.use_alias:
                summary = ", ".join([self.bible_data.aliases_version.get(v, v) for v in selected_versions])
            else:
                summary = ", ".join(selected_versions)
        else:
            summary = self.tr("msg_nothing")
            QMessageBox.warning(
                self,
                self.tr("warn_version_title"),
                self.tr("warn_version_msg")
            )
            self.book_combo.clear()
            self.chapter_input.clear()
            self.verse_input.clear()
            return

        self.version_summary_label.setText(summary)

        self.update_book_dropdown()

        for v in selected_versions:
            try:
                if v not in loaded_versions:
                    loaded_versions.append(v)
                    log_debug(f"[TabVerse] selected versions: {self.get_selected_versions()}")
            except Exception as e:
                log_error_with_dialog(e)
                QMessageBox.critical(self,
                    self.tr("error_loading_title"),
                    self.tr("error_loading_msg").format(v, e))


    def update_button_layout(self):
        """
        Updates the verse tab button layout dynamically based on polling and always-show settings.

        If polling is enabled or the "always show on/off buttons" setting is enabled,
        displays all 5 buttons (prev, search, save, next, clear).
        Otherwise, displays only 3 buttons (prev, search, next).
        """
        window_main = find_window_main(self)
        if not window_main:
            return

        poll_enabled = window_main.poll_toggle_btn.isChecked()
        always_show = window_main.settings.get("always_show_on_off_buttons", False)

        effective_polling = poll_enabled or always_show

        while self.button_layout.count():
            item = self.button_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        self.button_layout.addWidget(self.prev_verse_btn)
        self.button_layout.addWidget(self.search_btn)
        if effective_polling:
            self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.next_verse_btn)
        if effective_polling:
            self.button_layout.addWidget(self.clear_display_btn)


    def toggle_alias_mode(self):
        """
        Toggles between alias and full name display for versions.
        """
        self.use_alias = self.alias_toggle_btn.isChecked()
        if self.use_alias:
            self.alias_toggle_btn.setText(self.tr("label_alias_short"))
        else:
            self.alias_toggle_btn.setText(self.tr("label_alias_full"))
        self.update_version_summary()

    def handle_enter(self):
        """
        Handles Enter key behavior: alternating search/save.
        """
        if self.enter_state == 0:
            self.display_verse()
            self.enter_state = 1
        else:
            self.save_verse()
            self.enter_state = 0

    def get_reference(self):
        """
        Returns the resolved reference based on UI inputs.

        Returns:
            tuple: (versions, book, chapter, (start_verse, end_verse))
        """
        from core.logic.verse_logic import resolve_reference

        version_list = self.get_selected_versions()
        book_str = self.book_combo.currentText()
        chapter_str = self.chapter_input.currentText()
        verse_str = self.verse_input.text()
        return resolve_reference(version_list, book_str, chapter_str, verse_str, self.bible_data, self.current_language)

    def apply_output_text(self, text: str):
        """
        Displays the provided verse text in the display box with custom line height.
        """
        self.display_box.setText(text)

        cursor = self.display_box.textCursor()
        cursor.select(cursor.SelectionType.Document)

        block_format = QTextBlockFormat()
        block_format.setLineHeight(18.0, 4)  # Sets line spacing to approximately 150%
        cursor.setBlockFormat(block_format)

    def display_verse(self):
        """
        Displays the selected Bible verses by retrieving them from the data source.
        Delegates rendering to the display_verse_logic in verse_logic.
        """
        versions = self.get_selected_versions()
        if not versions:
            QMessageBox.warning(
                self,
                self.tr("warn_selection_title"),
                self.tr("error_no_version_selected")
            )
            return
        output = display_verse_logic(
            self.get_reference,
            self.verse_input,
            self.bible_data,
            self.tr,
            self.settings,
            self.current_language,
            self.apply_output_text
        )
        if output:
            self.formatted_verse_text = output

    def save_verse(self):
        """
        Saves the currently displayed verse text to file.
        """
        log_debug("[TabVerse] save_verse called")
        try:
            if not hasattr(self, "formatted_verse_text"):
                self.formatted_verse_text = ""
            save_to_files(self.formatted_verse_text, self.settings)
            log_debug("[TabVerse] verse saved successfully")
        except Exception as e:
            QMessageBox.critical(self,
                self.tr("error_saving_title"),
                self.tr("error_saving_msg").format(e))
            log_error_with_dialog("[TabVerse] failed to save verse")

    def shift_verse(self, delta):
        """
        Shifts to previous or next verse.

        Args:
            delta (int): Shift amount (positive or negative).
        """
        from core.logic.verse_logic import shift_verse_value

        versions, book, chapter, verse_range = self.get_reference()
        if not versions:
            return

        version = versions[0]
        book = resolve_book_name(book, self.bible_data, self.current_language)
        if book not in self.bible_data.get_verses(version):
            log_error_with_dialog(f"[TabVerse] Book '{book}' not found in version '{version}'")
            return

        try:
            if not isinstance(verse_range, tuple):
                log_error_with_dialog("[TabVerse] verse_range is not a tuple")
                return

            if verse_range[0] != verse_range[1]:
                QMessageBox.warning(self, 
                    self.tr("warn_jump_title"), 
                    self.tr("warn_jump_msg"))
                return

            current = verse_range[0]
            max_verse = get_max_verse(version, book, chapter)
            if max_verse == 0:
                QMessageBox.warning(self, 
                    self.tr("warn_no_chapter_title"), 
                    self.tr("warn_no_chapter_msg").format(book, chapter))
                return

            new_val = shift_verse_value(current, delta, max_verse)

            if new_val == 1 and current + delta < 1:
                QMessageBox.warning(self, 
                    self.tr("warn_range_title"), 
                    self.tr("warn_range_min"))
            elif new_val == max_verse and current + delta > max_verse:
                QMessageBox.warning(self, 
                    self.tr("warn_range_title"), 
                    self.tr("warn_range_max").format(max_verse))

            self.verse_input.setText(str(new_val))
            self.display_verse()

        except ValueError:
            log_error_with_dialog("[TabVerse] Invalid verse input.")
            QMessageBox.warning(
                self,
                self.tr("warn_verse_input_title"),
                self.tr("warn_verse_input_msg")
            )


    def get_selected_versions(self):
        """
        Returns the list of selected versions.

        Returns:
            list: Selected version names.
        """
        selected = []
        for i in range(self.version_layout.count()):
            widget = self.version_layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                selected.append(widget.version_key)
        return selected

    def get_common_books(self):
        """
        Finds common books among selected versions.

        Returns:
            list: Common books available.
        """
        from core.logic.verse_logic import get_common_books_among_versions

        versions = self.get_selected_versions()
        if not versions:
            return []

        common_books = get_common_books_among_versions(versions, self.bible_data.get_verses, self.bible_data)
        all_books = list(self.bible_data.standard_book.keys())
        return [b for b in all_books if b in common_books]


    def validate_selection(self):
        """
        Validates that versions and common books are available.

        Returns:
            tuple: (versions, common_books), or (None, None) if invalid.
        """
        from core.logic.verse_logic import validate_versions_and_books

        if getattr(self, "initializing", False):
            return self.get_selected_versions(), self.get_common_books()

        versions = self.get_selected_versions()
        validated_versions, common_books = validate_versions_and_books(versions, self.bible_data)

        return validated_versions, common_books

    def clear_outputs(self):
        """
        Clears the display box and output file.
        """
        self.display_box.clear()
        save_to_files("", self.settings)