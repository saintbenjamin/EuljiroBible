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

    def save_verse(self, formatted_verse_text):
        """
        Saves the currently displayed verse text to file.

        Args:
            formatted_verse_text (str): Text to be saved.
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
        Attempts to shift to the next or previous verse based on current input.

        Args:
            ref_func (callable): Returns (versions, book, chapter, verse_range, warning)
            verse_input_widget (QLineEdit): The input widget to update

        Returns:
            int | None: The new verse number, or None on failure
        """
        from core.logic.verse_logic import shift_verse_value
        from core.utils.bible_parser import resolve_book_name

        versions, book, chapter, verse_range, warning = ref_func()
        if not versions:
            return None

        version = versions[0]
        book = resolve_book_name(book, self.bible_data, self.current_language)
        if book not in self.bible_data.get_verses(version):
            raise Exception(f"Book '{book}' not found in version '{version}'")

        if not isinstance(verse_range, tuple):
            raise Exception("verse_range is not a tuple")

        if verse_range[0] != verse_range[1]:
            raise Exception("Cannot shift a verse range")

        current = verse_range[0]
        max_verse = self.bible_data.get_max_verse(version, book, chapter)
        if max_verse == 0:
            raise Exception(f"No verses found for {book} {chapter}")

        new_val = shift_verse_value(current, self.delta, max_verse)
        verse_input_widget.setText(str(new_val))
        return new_val