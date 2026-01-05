# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/ui/tab_verse.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Implements the :class:`gui.ui.tab_verse.TabVerse` class for verse lookup, navigation, display, and output.
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
from gui.utils.verse_output_handler import VerseOutputHandler

class TabVerse(QWidget, TabVerseUI):
    """
    GUI tab widget for Bible verse lookup, navigation, and export.

    This tab allows users to select one or more Bible versions, choose a book and
    chapter, enter verse ranges, preview formatted output, navigate between verses,
    and export the currently displayed verse to the configured overlay output file.

    The tab coordinates UI state, selection helpers, and backend logic components
    (TabVerseLogic, VerseVersionHelper, TabVerseSelectionManager, VerseOutputHandler).

    Attributes:
        tr (Callable[[str], str]): Translation function for UI labels and messages.
        settings (dict): Application-level settings dictionary.
        bible_data (BibleDataLoader): Bible data loader instance used for verse retrieval.
        version_layout (QGridLayout): Layout holding version selection checkboxes.
        version_helper (VerseVersionHelper): Helper for version selection and sorting.
        selection_manager (TabVerseSelectionManager): Helper for populating and syncing
            book/chapter/version UI elements.
        output_handler (VerseOutputHandler): Handler that applies formatted verse text
            to the main display widget and manages output formatting behavior.
        logic (TabVerseLogic): Backend verse display/export logic.
        version_list (list[str]): Available Bible versions used to populate UI controls.
        current_language (str): Current UI language code (e.g., "ko", "en").
        formatted_verse_text (str): Most recently formatted verse output (used for Enter key flow).
        enter_state (int): Enter-key state machine (0 = ready to display, 1 = ready to export).
        use_alias (bool): Whether to display version aliases instead of full version names.
    """
        # get_polling_status (Callable[[], bool]): Callback returning current polling toggle state.
        # get_always_show_setting (Callable[[], bool]): Callback returning current "always show buttons" toggle state.

    def __init__(self, version_list, settings, tr, get_polling_status=None, get_always_show_setting=None):
        """
        Initialize the TabVerse UI and connect backend helpers.

        This creates Bible data access, builds the version selection UI, initializes
        selection helpers and logic handlers, and installs UI signal connections for
        resetting Enter-state behavior when inputs change.

        Args:
            version_list (list[str]): Available Bible version identifiers.
            settings (dict): Loaded application settings.
            tr (Callable[[str], str]): Translation function for UI labels.
            get_polling_status (Callable[[], bool] | None): Optional callback that returns
                whether polling is active.
            get_always_show_setting (Callable[[], bool] | None): Optional callback that returns
                whether export/clear buttons should always be shown.
        """
        super().__init__()
        self.tr = tr
        self.initializing = False
        self.settings = settings
        self.formatted_verse_text = ""

        self.get_polling_status = get_polling_status or self.get_polling_status
        self.get_always_show_setting = get_always_show_setting or self.get_always_show_setting

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
        self.book_combo.currentTextChanged.connect(lambda _: self.reset_enter_state())
        self.chapter_input.currentIndexChanged.connect(lambda _: self.reset_enter_state())
        self.verse_input.textChanged.connect(lambda _: self.reset_enter_state())

    def change_language(self, lang_code):
        """
        Update UI labels and state to reflect a new language setting.

        This updates visible text, version summary rendering, book dropdown population,
        and button labels.

        Args:
            lang_code (str): Language code (e.g., "ko", "en").
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
        Handle resize events and recompute the version checkbox grid layout.

        Args:
            event (QResizeEvent): Resize event object.
        """
        super().resizeEvent(event)
        self.selection_manager.update_grid_layout(self)

    def update_button_layout(self):
        """
        Update the action button layout depending on effective polling state.

        Effective polling is defined as:
        polling enabled OR the "always show buttons" setting enabled.
        """
        poll_enabled = self.get_polling_status()
        always_show = self.get_always_show_setting()
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

    def get_polling_status(self):
        """
        Return the current polling toggle state.

        This method is designed to be overridden or replaced by an injected callback.

        Returns:
            bool: True if polling is enabled; otherwise False.
        """
        return False  # Default fallback, should be replaced by actual callback

    def get_always_show_setting(self):
        """
        Return the current "always show buttons" setting.

        This method is designed to be overridden or replaced by an injected callback.

        Returns:
            bool: True if export/clear buttons should always be visible; otherwise False.
        """
        return False  # Default fallback, should be replaced by actual callback

    def toggle_alias_mode(self):
        """
        Toggle between alias names and full names for Bible version display.

        This updates the alias mode flag, refreshes the toggle label, and updates the
        version summary accordingly.
        """
        self.use_alias = self.alias_toggle_btn.isChecked()
        self.alias_toggle_btn.setText(
            self.tr("label_alias_short") if self.use_alias else self.tr("label_alias_full")
        )
        self.update_version_summary(self)

    def handle_enter(self):
        """
        Handle Enter-key behavior as a two-step flow: display then export.

        If no formatted verse is currently staged, this displays the verse and caches
        the formatted output. If a formatted verse is already staged, this exports it
        to the output destination and resets the state machine.
        """
        if not self.formatted_verse_text:
            output = self.logic.display_verse(self.get_reference, self.verse_input, self.apply_output_text)
            if output:
                self.formatted_verse_text = output
                self.enter_state = 1
        else:
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
        Build and return the resolved verse reference tuple from current UI inputs.

        Returns:
            tuple: (versions, book, chapter, (start_verse, end_verse)) as produced by
                the shared reference resolver.
        """
        from core.logic.verse_logic import resolve_reference

        version_list = self.version_helper.get_selected_versions()
        book_str = self.book_combo.currentText()
        chapter_str = self.chapter_input.currentText()
        verse_str = self.verse_input.text()
        return resolve_reference(version_list, book_str, chapter_str, verse_str, self.bible_data, self.current_language)

    def apply_output_text(self, text: str):
        """
        Apply formatted verse output text to the main display.

        Args:
            text (str): Formatted text to display.
        """
        if text:
            self.formatted_verse_text = text
            self.output_handler.apply_output_text(text)

    def shift_verse(self, delta):
        """
        Shift the current verse number by a delta and refresh the displayed output.

        Args:
            delta (int): +1 for next verse, -1 for previous verse.
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

    def reset_enter_state(self):
        """
        Reset Enter-key state to the default "ready to display" mode.

        This clears any staged formatted verse output so the next Enter press performs
        a display operation.
        """
        self.enter_state = 0
        self.formatted_verse_text = ""

    def clear_outputs(self):
        """
        Clear the verse display and clear the output destination.

        This clears the UI display widget and writes an empty string to the configured
        output file(s) to stop any active overlay display.
        """
        self.display_box.clear()
        save_to_files("", self.settings)