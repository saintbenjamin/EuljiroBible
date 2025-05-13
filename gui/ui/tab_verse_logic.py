class TabVerseLogic:
    """
    Handles Bible verse logic such as displaying, saving, and shifting verses.
    """

    def __init__(self, bible_data, tr_func, settings, current_language):
        """
        Initializes logic class with shared data and config.

        Args:
            bible_data: Instance of BibleDataLoader.
            tr_func (callable): Translation function.
            settings (dict): Loaded user settings.
            current_language (str): Current language code (e.g., 'ko', 'en').
        """
        self.bible_data = bible_data
        self.tr = tr_func
        self.settings = settings
        self.current_language = current_language

    def display_verse(self, ref_func, verse_input, apply_output_text):
        """
        Displays the selected Bible verses by retrieving them from the data source.

        Args:
            ref_func (callable): Function that returns (versions, book, chapter, verse_range, warning)
            verse_input (QLineEdit): Input box for verse text
            apply_output_text (callable): Function to send output to display

        Returns:
            str | tuple | None: Rendered verse text, or warning message
        """
        from core.logic.verse_logic import display_verse_logic

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