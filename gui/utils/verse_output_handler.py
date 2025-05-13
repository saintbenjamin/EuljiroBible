from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextBlockFormat

from core.utils.utils_output import save_to_files

class VerseOutputHandler:
    """
    Handles output display and saving logic for Bible verses.
    """

    def __init__(self, display_box: QTextEdit, settings: dict):
        """
        Initialize the output handler with display widget and settings.

        Args:
            display_box (QTextEdit): The display area for formatted verses.
            settings (dict): App configuration for output path etc.
        """
        self.display_box = display_box
        self.settings = settings

    def apply_output_text(self, text: str):
        """
        Display text in the verse output box with custom line spacing.

        Args:
            text (str): Formatted verse string to display.
        """
        self.display_box.setText(text)

        cursor = self.display_box.textCursor()
        cursor.select(cursor.SelectionType.Document)

        block_format = QTextBlockFormat()
        block_format.setLineHeight(18.0, 4)  # Approximately 150% line spacing
        cursor.setBlockFormat(block_format)

    def save_verse(self, formatted_text: str):
        """
        Save formatted verse text to output file.

        Args:
            formatted_text (str): Verse text to save.
        """
        if not formatted_text:
            formatted_text = ""
        save_to_files(formatted_text, self.settings)