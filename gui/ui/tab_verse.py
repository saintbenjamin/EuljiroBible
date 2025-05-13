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

from PySide6.QtWidgets import QWidget, QMessageBox, QGridLayout

from core.logic.verse_logic import display_verse_logic
from core.utils.bible_data_loader import BibleDataLoader
from core.utils.bible_parser import resolve_book_name
from core.utils.logger import log_debug
from core.utils.utils_output import save_to_files
from core.utils.verse_version_helper import VerseVersionHelper

from gui.ui.locale.message_loader import load_messages
from gui.ui.tab_verse_logic import TabVerseLogic
from gui.ui.tab_verse_selection_manager import TabVerseSelectionManager
from gui.ui.tab_verse_ui import TabVerseUI
from gui.utils.logger import log_error_with_dialog
from gui.utils.utils_window import find_window_main
from gui.utils.verse_output_handler import VerseOutputHandler


class TabVerse(QWidget, TabVerseUI):
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
        self.version_layout = QGridLayout()
        self.version_helper = VerseVersionHelper(self.bible_data, self.version_layout)
        self.selection_manager = TabVerseSelectionManager(self.bible_data, self.version_helper, self.tr)

        self.version_list = version_list
        self.init_ui(version_list)

        self.version_helper.version_layout = self.version_layout

        self.version_list = self.version_helper.sort_versions(version_list)
        self.output_handler = VerseOutputHandler(self.display_box, self.settings)

        self.current_language = settings.get("last_language", "ko")
        self.logic = TabVerseLogic(self.bible_data, self.tr, self.settings, self.current_language)

    def change_language(self, lang_code):
        """
        Changes the UI language dynamically.

        Args:
            lang_code (str): Language code.
        """
        self.current_language = lang_code
        self.messages = load_messages(lang_code)

        selected_versions = self.version_helper.get_selected_versions()

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

        self.selection_manager.populate_book_dropdown(self)

        if hasattr(self, "alias_toggle_btn"):
            if self.use_alias:
                self.alias_toggle_btn.setText(self.tr("label_alias_short"))
            else:
                self.alias_toggle_btn.setText(self.tr("label_alias_full"))

        self.selection_manager.update_book_dropdown(self, self.current_language)

        self.prev_verse_btn.setText(self.tr("btn_prev"))
        self.search_btn.setText(self.tr("btn_search"))
        self.save_btn.setText(self.tr("btn_output"))
        self.next_verse_btn.setText(self.tr("btn_next"))
        self.clear_display_btn.setText(self.tr("btn_clear"))

    def resizeEvent(self, event):
        """
        Handles window resize to adjust grid layout.

        Args:
            event (QResizeEvent): Resize event.
        """
        super().resizeEvent(event)
        self.selection_manager.update_grid_layout(self)


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
        self.update_version_summary(self)

    def handle_enter(self):
        """
        Handles Enter key behavior: alternating search/save.
        """
        if self.enter_state == 0:
            output = self.logic.display_verse(
                self.get_reference,
                self.verse_input,
                self.apply_output_text
            )
            if output:
                self.formatted_verse_text = output
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

        version_list = self.version_helper.get_selected_versions()
        book_str = self.book_combo.currentText()
        chapter_str = self.chapter_input.currentText()
        verse_str = self.verse_input.text()
        return resolve_reference(version_list, book_str, chapter_str, verse_str, self.bible_data, self.current_language)

    def apply_output_text(self, text: str):
        """
        Displays the provided verse text in the display box with custom line height.
        """
        if text:
            self.formatted_verse_text = text
            self.output_handler.apply_output_text(text)

    def display_verse(self):
        """
        Displays the selected Bible verses by retrieving them from the data source.
        Delegates rendering to the display_verse_logic in verse_logic.
        """
        versions = self.version_helper.get_selected_versions()
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
            self.output_handler.save_verse(self.formatted_verse_text)
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

        versions, book, chapter, verse_range, warning = self.get_reference()
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
            max_verse = self.bible_data.get_max_verse(version, book, chapter)
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
            output = self.logic.display_verse(
                self.get_reference,
                self.verse_input,
                self.apply_output_text
            )
            if output:
                self.formatted_verse_text = output

        except ValueError:
            log_error_with_dialog("[TabVerse] Invalid verse input.")
            QMessageBox.warning(
                self,
                self.tr("warn_verse_input_title"),
                self.tr("warn_verse_input_msg")
            )

    def clear_outputs(self):
        """
        Clears the display box and output file.
        """
        self.display_box.clear()
        save_to_files("", self.settings)