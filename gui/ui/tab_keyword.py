# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/ui/tab_keyword.py
Implements the TabKeyword for EuljiroBible, enabling Bible keyword search, result display, and verse export.

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
    Tab for searching Bible verses by keywords, displaying results, and exporting selected verses.
    """

    def __init__(self, version_list, settings, tr):
        """
        Initializes the TabKeyword.

        Args:
            version_list (list): List of available Bible versions.
            settings (dict): Loaded user settings.
            tr (function): Translation function.
        """
        super().__init__()
        self.tr = tr     # Translation function for UI strings
        self.settings = settings  # Loaded configuration settings
        self.current_language = "ko"
        self.bible_data = BibleDataLoader()  # Load Bible metadata

        self.logic = TabKeywordLogic(settings, tr)

        self.init_ui(version_list=version_list)

    def change_language(self, lang_code):
        """
        Changes the UI language dynamically.

        Args:
            lang_code (str): Language code.
        """
        self.current_language = lang_code
        self.messages = load_messages(lang_code)
        self.keyword_input.setPlaceholderText(self.tr("search_keyword_hint"))
        self.search_button.setText(self.tr("btn_search"))
        self.select_button.setText(self.tr("btn_output"))
        self.clear_button.setText(self.tr("btn_clear"))
        self.table.setHorizontalHeaderLabels([self.tr("search_location"), self.tr("search_verse")])
        self.summary_title_label.setText(self.tr("search_summary"))
        self.summary_box.setPlaceholderText(self.tr("search_summary"))

    def run_search(self):
        self.logic.run_search(self)

    def save_selected_verse(self):
        self.logic.save_selected_verse(self)

    def clear_outputs(self):
        self.logic.clear_outputs(self)   

    def update_table(self, results):
        self.logic.update_table(self, results)

    def update_summary(self, counts):
        self.logic.update_summary(self, counts)