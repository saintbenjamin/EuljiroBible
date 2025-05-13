# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_verse.py
Implements the TabVerse class for verse lookup, navigation, display, and output.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import traceback
from PySide6.QtWidgets import QWidget, QMessageBox, QGridLayout

from core.utils.bible_data_loader import BibleDataLoader
from core.utils.utils_output import save_to_files
from core.utils.verse_version_helper import VerseVersionHelper
from gui.ui.locale.message_loader import load_messages
from gui.ui.tab_verse_logic import TabVerseLogic
from gui.ui.tab_verse_selection_manager import TabVerseSelectionManager
from gui.ui.tab_verse_ui import TabVerseUI
from gui.utils.utils_window import find_window_main
from gui.utils.verse_output_handler import VerseOutputHandler


class TabVerse(QWidget, TabVerseUI):
    """
    Main UI class for the Bible verse tab.
    Provides display, navigation, and save functionality for selected verses.
    """

    def __init__(self, version_list, settings, tr):
        """
        Initialize the TabVerse.

        :param version_list: Available Bible versions
        :type version_list: list[str]
        :param settings: Loaded application settings
        :type settings: dict
        :param tr: Translation function
        :type tr: Callable[[str], str]
        """
        super().__init__()
        self.tr = tr
        self.initializing = False
        self.settings = settings
        self.formatted_verse_text = ""

        # Load Bible data and UI components
        self.bible_data = BibleDataLoader()
        self.version_layout = QGridLayout()
        self.version_helper = VerseVersionHelper(self.bible_data, self.version_layout)
        self.selection_manager = TabVerseSelectionManager(self.bible_data, self.version_helper, self.tr)

        self.version_list = version_list
        self.init_ui(version_list)

        # Re-assign layout after UI build
        self.version_helper.version_layout = self.version_layout

        # Sort versions and assign logic handlers
        self.version_list = self.version_helper.sort_versions(version_list)
        self.output_handler = VerseOutputHandler(self.display_box, self.settings)

        self.current_language = settings.get("last_language", "ko")
        self.logic = TabVerseLogic(self.bible_data, self.tr, self.settings, self.current_language)

    def change_language(self, lang_code):
        """
        Dynamically updates UI labels when the language changes.

        :param lang_code: Language code ('ko' or 'en')
        :type lang_code: str
        """
        self.current_language = lang_code
        self.messages = load_messages(lang_code)

        selected_versions = self.version_helper.get_selected_versions()
        summary = (
            ", ".join([self.bible_data.aliases_version.get(v, v) for v in selected_versions])
            if selected_versions and self.use_alias else
            ", ".join(selected_versions) if selected_versions else
            self.tr("msg_nothing")
        )
        self.version_summary_label.setText(summary)

        # Update labels and placeholders
        self.book_label.setText(self.tr("label_book"))
        self.chapter_label.setText(self.tr("label_chapter"))
        self.verse_label.setText(self.tr("label_verse"))
        self.verse_input.setPlaceholderText(self.tr("verse_input_hint"))

        self.selection_manager.populate_book_dropdown(self)

        if hasattr(self, "alias_toggle_btn"):
            self.alias_toggle_btn.setText(
                self.tr("label_alias_short") if self.use_alias else self.tr("label_alias_full")
            )

        self.selection_manager.update_book_dropdown(self, self.current_language)

        # Update button texts
        self.prev_verse_btn.setText(self.tr("btn_prev"))
        self.search_btn.setText(self.tr("btn_search"))
        self.save_btn.setText(self.tr("btn_output"))
        self.next_verse_btn.setText(self.tr("btn_next"))
        self.clear_display_btn.setText(self.tr("btn_clear"))

    def resizeEvent(self, event):
        """
        Responds to window resize events and updates the version layout.

        :param event: Resize event object
        :type event: QResizeEvent
        """
        super().resizeEvent(event)
        self.selection_manager.update_grid_layout(self)

    def update_button_layout(self):
        """
        Updates the layout of the action buttons depending on polling mode.
        """
        window_main = find_window_main(self)
        if not window_main:
            return

        poll_enabled = window_main.poll_toggle_btn.isChecked()
        always_show = window_main.settings.get("always_show_on_off_buttons", False)
        effective_polling = poll_enabled or always_show

        # Clear all existing buttons
        while self.button_layout.count():
            item = self.button_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Re-add buttons based on conditions
        self.button_layout.addWidget(self.prev_verse_btn)
        self.button_layout.addWidget(self.search_btn)
        if effective_polling:
            self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.next_verse_btn)
        if effective_polling:
            self.button_layout.addWidget(self.clear_display_btn)

    def toggle_alias_mode(self):
        """
        Toggles between alias name and full name for Bible versions.
        """
        self.use_alias = self.alias_toggle_btn.isChecked()
        self.alias_toggle_btn.setText(
            self.tr("label_alias_short") if self.use_alias else self.tr("label_alias_full")
        )
        self.update_version_summary(self)

    def handle_enter(self):
        """
        Handles Enter key logic for alternating between search and save.
        """
        if self.enter_state == 0:
            # Display verse
            output = self.logic.display_verse(self.get_reference, self.verse_input, self.apply_output_text)
            if output:
                self.formatted_verse_text = output
            self.enter_state = 1
        else:
            # Save verse
            try:
                self.logic.save_verse(self.formatted_verse_text)
            except Exception as e:
                print(traceback.format_exc())
                QMessageBox.critical(
                    self,
                    self.tr("error_output_title"),
                    self.tr("error_output_msg").format(str(e))
                )
            self.enter_state = 0

    def get_reference(self):
        """
        Returns parsed reference from the input fields.

        :return: (versions, book, chapter, (start_verse, end_verse))
        :rtype: tuple
        """
        from core.logic.verse_logic import resolve_reference

        version_list = self.version_helper.get_selected_versions()
        book_str = self.book_combo.currentText()
        chapter_str = self.chapter_input.currentText()
        verse_str = self.verse_input.text()
        return resolve_reference(version_list, book_str, chapter_str, verse_str, self.bible_data, self.current_language)

    def apply_output_text(self, text: str):
        """
        Displays formatted verse text in the main display box.

        :param text: Formatted text to show
        :type text: str
        """
        if text:
            self.formatted_verse_text = text
            self.output_handler.apply_output_text(text)

    def shift_verse(self, delta):
        """
        Changes the current verse number up/down and displays the result.

        :param delta: +1 for next, -1 for previous
        :type delta: int
        """
        try:
            self.logic.delta = delta
            new_val = self.logic.shift_verse(self.get_reference, self.verse_input)
            if new_val:
                output = self.logic.display_verse(self.get_reference, self.verse_input, self.apply_output_text)
                if output:
                    self.formatted_verse_text = output
        except Exception:
            QMessageBox.warning(
                self,
                self.tr("warn_jump_title"),
                self.tr("warn_jump_msg")
            )

    def clear_outputs(self):
        """
        Clears the displayed verse and the output file.
        """
        self.display_box.clear()
        save_to_files("", self.settings)