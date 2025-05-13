# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_keyword.py
Implements the TabKeyword class for EuljiroBible, enabling Bible keyword search, result display, and verse export.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtWidgets import QWidget

from core.utils.bible_data_loader import BibleDataLoader
from gui.ui.locale.message_loader import load_messages
from gui.ui.tab_keyword_logic import TabKeywordLogic
from gui.ui.tab_keyword_ui import TabKeywordUI


class TabKeyword(QWidget, TabKeywordUI):
    """
    Tab class for performing Bible keyword searches.

    Displays results in a table, allows verse export, and supports multilingual UI updates.
    """

    def __init__(self, version_list, settings, tr):
        """
        Initialize the keyword tab UI and logic layer.

        :param version_list: List of available Bible versions
        :type version_list: list[str]
        :param settings: Shared user settings
        :type settings: dict
        :param tr: Translation function for multilingual UI
        :type tr: Callable[[str], str]
        """
        super().__init__()
        self.tr = tr                          # Translation function for labels
        self.settings = settings              # Loaded application configuration
        self.current_language = "ko"          # Default language
        self.bible_data = BibleDataLoader()   # Bible version and book metadata

        self.logic = TabKeywordLogic(settings, tr)  # Search and logic backend

        self.init_ui(version_list=version_list)     # Construct layout

    def change_language(self, lang_code):
        """
        Dynamically update all UI elements for the specified language.

        :param lang_code: Target language code ('ko' or 'en')
        :type lang_code: str
        """
        self.current_language = lang_code
        self.messages = load_messages(lang_code)

        # Update placeholder and all text labels
        self.keyword_input.setPlaceholderText(self.tr("search_keyword_hint"))
        self.search_button.setText(self.tr("btn_search"))
        self.select_button.setText(self.tr("btn_output"))
        self.clear_button.setText(self.tr("btn_clear"))
        self.table.setHorizontalHeaderLabels([self.tr("search_location"), self.tr("search_verse")])
        self.summary_title_label.setText(self.tr("search_summary"))
        self.summary_box.setPlaceholderText(self.tr("search_summary"))

    def run_search(self):
        """
        Triggers a keyword search using current input and version.

        Delegates to `TabKeywordLogic.run_search()`.
        """
        self.logic.run_search(self)

    def save_selected_verse(self):
        """
        Saves the currently selected verse in the result table to output file.

        Delegates to `TabKeywordLogic.save_selected_verse()`.
        """
        self.logic.save_selected_verse(self)

    def clear_outputs(self):
        """
        Clears the saved verse output file and display fields.

        Delegates to `TabKeywordLogic.clear_outputs()`.
        """
        self.logic.clear_outputs(self)

    def update_table(self, results):
        """
        Updates the table widget with new search results.

        :param results: List of search result entries
        :type results: list[dict]
        """
        self.logic.update_table(self, results)

    def update_summary(self, counts):
        """
        Displays keyword count summary in the summary box.

        :param counts: Mapping of keyword -> hit count
        :type counts: dict[str, int]
        """
        self.logic.update_summary(self, counts)