# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/verse_output_handler.py
Handles text display and file saving for formatted Bible verses in the GUI.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextBlockFormat

from core.utils.utils_output import save_to_files


class VerseOutputHandler:
    """
    Manages displaying and saving Bible verse text in the GUI.

    :param display_box: QTextEdit widget where verses will be shown
    :type display_box: QTextEdit
    :param settings: Application settings dictionary
    :type settings: dict
    """

    def __init__(self, display_box: QTextEdit, settings: dict):
        """
        Initialize the handler with the display box and configuration.

        :param display_box: The QTextEdit area for displaying verse output
        :type display_box: QTextEdit
        :param settings: Dictionary containing application settings (e.g. output path)
        :type settings: dict
        """
        self.display_box = display_box
        self.settings = settings

    def apply_output_text(self, text: str):
        """
        Display the given verse text in the output box with proper formatting.

        Applies a block format with approximately 150% line spacing.

        :param text: The verse string to render
        :type text: str
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
        Save the formatted verse text to the file(s) specified in settings.

        :param formatted_text: The string of formatted verses
        :type formatted_text: str
        """
        # If text is empty or None, treat it as empty string
        if not formatted_text:
            formatted_text = ""

        # Delegate to output utility to save the content
        save_to_files(formatted_text, self.settings)