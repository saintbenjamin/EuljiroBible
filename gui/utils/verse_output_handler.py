# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/verse_output_handler.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Handles text display and file saving for formatted Bible verses in the GUI.
"""

from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextBlockFormat

from core.utils.utils_output import save_to_files


class VerseOutputHandler:
    """
    Manages displaying and saving Bible verse text in the GUI.

    This class is responsible for:

    - Rendering formatted Bible verse text into a QTextEdit widget.
    - Applying consistent paragraph formatting (e.g. line spacing).
    - Delegating persistence of verse output to file-based utilities.

    Attributes:
        display_box (QTextEdit):
            Text edit widget used to display verse output to the user.
        settings (dict):
            Application settings dictionary. This typically includes output
            paths and related configuration used when saving verse text.
    """

    def __init__(self, display_box: QTextEdit, settings: dict):
        """
        Initialize the handler with the display widget and configuration.

        Args:
            display_box (QTextEdit):
                QTextEdit area for displaying verse output.
            settings (dict):
                Dictionary containing application settings
                (e.g. output paths, polling options).
        """
        self.display_box = display_box
        self.settings = settings

    def apply_output_text(self, text: str):
        """
        Display the given verse text in the output box with formatting applied.

        The text is rendered into the QTextEdit and a block format is applied
        to enforce approximately 150% line spacing across the entire document.

        Args:
            text (str):
                Verse text to render in the output box.
        """
        # Insert the formatted verse text into the text box
        self.display_box.setText(text)

        # Apply 150% line spacing to the entire document
        cursor = self.display_box.textCursor()
        cursor.select(cursor.SelectionType.Document)

        block_format = QTextBlockFormat()
        block_format.setLineHeight(18.0, 4)  # Fixed height, multiplier mode
        cursor.setBlockFormat(block_format)

    def save_verse(self, formatted_text: str):
        """
        Save the formatted verse text to output file(s).

        If the provided text is empty or None, it is treated as an empty string.
        Actual file writing is delegated to the output utility layer.

        Args:
            formatted_text (str):
                Formatted verse text to be saved.
        """
        # If text is empty or None, treat it as empty string
        if not formatted_text:
            formatted_text = ""

        # Delegate to output utility to save the content
        save_to_files(formatted_text, self.settings)