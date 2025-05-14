# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_keyword.py
Implements the TabKeyword class for EuljiroBible, enabling Bible keyword search,
search result rendering, multilingual updates, and verse output handling.

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
    GUI tab class for Bible keyword searching.

    Provides multilingual keyword search, result table display,
    summary box update, and verse export functionality.
    """

    def __init__(self, version_list, settings, tr,
                 get_polling_status=None, get_always_show_setting=None):
        """
        Initialize the TabKeyword UI, logic, and Bible data.

        :param version_list: Available Bible version list
        :type version_list: list[str]
        :param settings: Application-level settings
        :type settings: dict
        :param tr: Translation function for UI labels
        :type tr: Callable[[str], str]
        :param get_polling_status: Optional callback to get polling state
        :type get_polling_status: Callable[[], bool] or None
        :param get_always_show_setting: Optional callback for always-show-button toggle
        :type get_always_show_setting: Callable[[], bool] or None
        """
        super().__init__()
        self.tr = tr
        self.settings = settings
        self.current_language = "ko"
        self.bible_data = BibleDataLoader()
        self.logic = TabKeywordLogic(settings, tr)

        # Inject fallback functions if not provided
        self.get_polling_status = get_polling_status or self.get_polling_status
        self.get_always_show_setting = get_always_show_setting or self.get_always_show_setting

        # Build layout
        self.init_ui(
            version_list=version_list,
            get_polling_status=self.get_polling_status,
            get_always_show_setting=self.get_always_show_setting
        )

    def change_language(self, lang_code):
        """
        Update UI text and placeholder strings according to selected language.

        :param lang_code: Language code ('ko', 'en', etc.)
        :type lang_code: str
        """
        self.current_language = lang_code
        self.messages = load_messages(lang_code)

        # Update all visible UI elements
        self.radio_and.setText(self.tr("search_mode_all"))
        self.radio_compact.setText(self.tr("search_mode_compact"))
        self.keyword_input.setPlaceholderText(self.tr("search_keyword_hint"))
        self.search_button.setText(self.tr("btn_search"))
        self.select_button.setText(self.tr("btn_output"))
        self.clear_button.setText(self.tr("btn_clear"))
        self.summary_title_label.setText(self.tr("search_summary"))
        self.summary_box.setPlaceholderText(self.tr("search_summary"))

    def run_search(self):
        """
        Trigger a keyword search using the logic backend.
        """
        self.logic.run_search(self)

    def save_selected_verse(self):
        """
        Save the currently selected verse to verse_output.txt
        for overlay usage or exporting.
        """
        self.logic.save_selected_verse(self)

    def clear_outputs(self):
        """
        Clear the verse output file and reset summary/preview fields.
        """
        self.logic.clear_outputs(self)

    def update_table(self, results):
        """
        Update the keyword result table with new entries.

        :param results: List of result dictionaries
        :type results: list[dict]
        """
        self.logic.update_table(self, results)

    def update_summary(self, counts):
        """
        Update the summary box with keyword occurrence counts.

        :param counts: Keyword → count dictionary
        :type counts: dict[str, int]
        """
        self.logic.update_summary(self, counts)

    def get_polling_status(self):
        """
        Return the current polling toggle state.
        Overridable callback for external control.

        :return: True if polling is active
        :rtype: bool
        """
        return False

    def get_always_show_setting(self):
        """
        Return the current 'always show buttons' setting.
        Overridable callback for external control.

        :return: True if buttons are always shown
        :rtype: bool
        """
        return False
