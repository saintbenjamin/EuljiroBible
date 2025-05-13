# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/tab_verse_logic.py
Provides logic for verse display, saving, and verse shifting for the TabVerse UI.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""


class TabVerseLogic:
    """
    Contains logic to handle displaying, saving, and navigating Bible verses in the UI.

    :param bible_data: Instance of BibleDataLoader containing Bible content
    :type bible_data: BibleDataLoader
    :param tr_func: Translation function used for localized UI messages
    :type tr_func: Callable[[str], str]
    :param settings: Configuration settings for verse output
    :type settings: dict
    :param current_language: Active language code (e.g., 'en', 'ko')
    :type current_language: str
    """

    def __init__(self, bible_data, tr_func, settings, current_language):
        """
        Initialize the logic handler with dependencies.

        :param bible_data: Bible data instance
        :param tr_func: Translation function
        :param settings: Application settings dictionary
        :param current_language: Current UI language code
        """
        self.bible_data = bible_data
        self.tr = tr_func
        self.settings = settings
        self.current_language = current_language

    def display_verse(self, ref_func, verse_input, apply_output_text):
        """
        Renders and returns a formatted Bible verse using internal display logic.

        :param ref_func: Function returning (versions, book, chapter, verse_range, warning)
        :type ref_func: Callable
        :param verse_input: Input box containing the verse reference
        :type verse_input: QLineEdit
        :param apply_output_text: Callback to apply rendered text to the UI
        :type apply_output_text: Callable
        :return: Final rendered verse text, or None if failed
        :rtype: str | tuple | None
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
        Saves the formatted verse to the configured output file.

        :param formatted_verse_text: Verse text to save
        :type formatted_verse_text: str
        :raises Exception: If saving fails
        """
        from core.utils.utils_output import save_to_files

        try:
            text = formatted_verse_text or ""
            save_to_files(text, self.settings)
        except Exception as e:
            raise Exception(f"Failed to save verse: {e}")

    def shift_verse(self, ref_func, verse_input_widget):
        """
        Shifts to the previous or next verse depending on `self.delta`.

        :param ref_func: Function returning (versions, book, chapter, verse_range, warning)
        :type ref_func: Callable
        :param verse_input_widget: The input widget to update with new verse
        :type verse_input_widget: QLineEdit
        :return: New verse number or None if shifting is not possible
        :rtype: int | None
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