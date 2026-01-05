# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/ui/tab_verse_logic.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Provides logic for verse display, saving, and verse shifting for the :class:`gui.ui.tab_verse.TabVerse` UI.
"""

class TabVerseLogic:
    """
    Backend logic for displaying, exporting, and navigating Bible verses.

    This class provides the non-UI operations used by the TabVerse GUI tab. It
    delegates complex formatting and parsing to shared logic functions while
    holding the dependencies required for verse retrieval, localization, and
    output persistence.

    Attributes:
        bible_data (BibleDataLoader): Bible data loader instance used to access verse content.
        tr (Callable[[str], str]): Translation function used for localized UI messages.
        settings (dict): Application settings dictionary used for output persistence.
        current_language (str): Active UI language code (e.g., "ko", "en").
        delta (int): Verse navigation direction used by shift_verse
            (+1 for next, -1 for previous). This is set externally by the UI layer.
    """

    def __init__(self, bible_data, tr_func, settings, current_language):
        """
        Initialize the logic handler with dependencies.

        Args:
            bible_data (BibleDataLoader): Bible data loader instance containing Bible content.
            tr_func (Callable[[str], str]): Translation function for localized UI strings.
            settings (dict): Application settings dictionary used for output.
            current_language (str): Current UI language code (e.g., "ko", "en").
        """
        self.bible_data = bible_data
        self.tr = tr_func
        self.settings = settings
        self.current_language = current_language

    def display_verse(self, ref_func, verse_input, apply_output_text):
        """
        Render and return formatted verse text for the current UI reference.

        This delegates to the shared verse display implementation, injecting the
        current dependencies (bible_data, translation function, settings, language)
        and a callback for applying output to the UI.

        Args:
            ref_func (Callable[[], tuple]): Callback returning the current resolved reference.
                Expected to return a tuple like:
                (versions, book, chapter, verse_range, warning).
            verse_input (QLineEdit): Verse input widget (used by the shared display logic).
            apply_output_text (Callable[[str], None]): Callback that applies rendered text to the UI.

        Returns:
            str | tuple | None: Rendered verse output, or None if display failed.
        """
        from core.logic.verse_logic import display_verse_logic

        # Invoke display logic with injected dependencies
        output = display_verse_logic(
            ref_func,
            verse_input,
            self.bible_data,
            self.tr,
            self.settings,
            self.current_language,
            apply_output_text
        )
        return output

    def save_verse(self, formatted_verse_text):
        """
        Save formatted verse text to the configured output destination.

        Args:
            formatted_verse_text (str): Verse text to save. If empty/None, an empty string is written.

        Raises:
            Exception: If saving fails.
        """
        from core.utils.utils_output import save_to_files

        try:
            text = formatted_verse_text or ""
            save_to_files(text, self.settings)
        except Exception as e:
            raise Exception(f"Failed to save verse: {e}")

    def shift_verse(self, ref_func, verse_input_widget):
        """
        Shift the current verse number by self.delta and update the input widget.

        This validates that a single verse is selected (not a range), determines the
        maximum verse count for the chapter, computes the new verse number, and writes
        it back into the verse input widget.

        Args:
            ref_func (Callable[[], tuple]): Callback returning the current resolved reference.
                Expected to return: (versions, book, chapter, verse_range, warning).
            verse_input_widget (QLineEdit): Verse input widget to update with the new verse number.

        Returns:
            int | None: New verse number if shifting succeeds; otherwise None.

        Raises:
            Exception: If reference data is invalid, the book/chapter cannot be resolved,
                or shifting is not possible (e.g., verse range selected).
        """
        from core.logic.verse_logic import shift_verse_value
        from core.utils.bible_parser import resolve_book_name

        # Extract reference info from ref_func
        versions, book, chapter, verse_range, warning = ref_func()
        if not versions:
            return None

        version = versions[0]

        # Normalize book name using internal parser
        book = resolve_book_name(book, self.bible_data, self.current_language)
        if book not in self.bible_data.get_verses(version):
            raise Exception(f"Book '{book}' not found in version '{version}'")

        if not isinstance(verse_range, tuple):
            raise Exception("verse_range is not a tuple")

        if verse_range[0] != verse_range[1]:
            raise Exception("Cannot shift a verse range")

        # Extract and validate current verse number
        current = verse_range[0]
        max_verse = self.bible_data.get_max_verse(version, book, chapter)
        if max_verse == 0:
            raise Exception(f"No verses found for {book} {chapter}")

        # Calculate and apply new verse number
        new_val = shift_verse_value(current, self.delta, max_verse)
        verse_input_widget.setText(str(new_val))
        return new_val