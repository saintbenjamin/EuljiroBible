# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/ui/tab_keyword.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Implements the :class:`gui.ui.tab_keyword.TabKeyword` class for EuljiroBible, enabling Bible keyword search,
search result rendering, multilingual updates, and verse output handling.
"""

from PySide6.QtWidgets import QWidget

from core.utils.bible_data_loader import BibleDataLoader
from gui.ui.locale.message_loader import load_messages
from gui.ui.tab_keyword_logic import TabKeywordLogic
from gui.ui.tab_keyword_ui import TabKeywordUI

class TabKeyword(QWidget, TabKeywordUI):
    """
    GUI tab widget for Bible keyword searching.

    This tab provides a multilingual keyword search workflow backed by
    TabKeywordLogic, including result table rendering, summary updates,
    and exporting the selected verse for overlay usage.

    Attributes:
        tr (Callable[[str], str]): Translation function for UI labels and messages.
        settings (dict): Application-level settings dictionary.
        current_language (str): Current UI language code (e.g., "ko", "en").
        bible_data (BibleDataLoader): Bible data loader instance used by this tab.
        logic (TabKeywordLogic): Backend logic handler for search and export actions.

    Note:
        The following callables are intentionally *not* listed under ``Attributes`` to
        avoid duplicate autodoc entries, as they are already documented as class methods:

        - get_polling_status (Callable[[], bool]): Callback returning the current polling state.
        - get_always_show_setting (Callable[[], bool]): Callback returning the current "always show buttons" toggle state.
    """

    def __init__(self, version_list, settings, tr,
                 get_polling_status=None, get_always_show_setting=None):
        """
        Initialize the TabKeyword UI, logic backend, and Bible data.

        Args:
            version_list (List[str]): Available Bible version list shown in the UI.
            settings (dict): Application-level settings.
            tr (Callable[[str], str]): Translation function for UI labels.
            get_polling_status (Callable[[], bool] | None): Optional callback to retrieve
                polling state. If not provided, a default stub method is used.
            get_always_show_setting (Callable[[], bool] | None): Optional callback to retrieve
                the "always show buttons" state. If not provided, a default stub method is used.
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
        Update UI text and placeholder strings according to the selected language.

        Args:
            lang_code (str): Language code (e.g., "ko", "en").
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
        Save the currently selected verse to the overlay output file.

        This delegates to the logic backend, which writes the selected verse to
        the configured verse output destination (e.g., verse_output.txt) for overlay
        usage or exporting.
        """
        self.logic.save_selected_verse(self)

    def clear_outputs(self):
        """
        Clear the verse output destination and reset summary/preview fields.

        This delegates to the logic backend to clear the output file and reset
        UI state as needed.
        """
        self.logic.clear_outputs(self)

    def update_table(self, results):
        """
        Update the keyword result table with new entries.

        Args:
            results (List[dict]): List of result dictionaries produced by the search backend.
        """
        self.logic.update_table(self, results)

    def update_summary(self, counts):
        """
        Update the summary box with keyword occurrence counts.

        Args:
            counts (Dict[str, int]): Mapping from keyword to occurrence count.
        """
        self.logic.update_summary(self, counts)

    def get_polling_status(self):
        """
        Return the current polling toggle state.

        This method is designed to be overridden or replaced by an injected callback.

        Returns:
            bool: True if polling is active; otherwise False.
        """
        return False

    def get_always_show_setting(self):
        """
        Return the current "always show buttons" setting.

        This method is designed to be overridden or replaced by an injected callback.

        Returns:
            bool: True if buttons are always shown; otherwise False.
        """
        return False