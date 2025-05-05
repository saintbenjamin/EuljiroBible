# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/bible_data_loader.py
Handles lazy loading and caching of Bible text and metadata from JSON sources.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import os
import json

from core.config import paths
from core.utils.logger import log_error


class BibleDataLoader:
    """
    Loads and lazily caches Bible-related JSON data: version aliases, book aliases, canonical names,
    and full Bible texts.

    Lazy-loading ensures performance is optimized by only loading data on-demand.
    """

    def __init__(self, json_dir=None, text_dir=None):
        """
        Initializes the data loader with optional override paths.

        Args:
            json_dir (str, optional): Path to JSON metadata files.
            text_dir (str, optional): Path to Bible text JSON files.
        """
        self.json_dir = json_dir or paths.BIBLE_NAME_DIR
        self.text_dir = text_dir or paths.BIBLE_DATA_DIR

        # Load version and book aliases, canonical book names, and sort order
        self.aliases_version = self._load_json(os.path.join(self.json_dir, "aliases_version.json"))
        self.aliases_book = self._load_json(os.path.join(self.json_dir, "aliases_book.json"))
        self.standard_book = self._load_json(os.path.join(self.json_dir, "standard_book.json"))
        self.sort_order = self._load_json(os.path.join(self.json_dir, "your_sort_order.json"))

        self.data = {}  # Cache for loaded Bible texts

    def get_verses(self, version):
        """
        Retrieves all verses for a given Bible version, loading from disk if needed.

        Args:
            version (str): Version key (e.g. "KJV", "NKRV")

        Returns:
            dict: Full nested dict of verses for the version
        """
        if version not in self.data:
            try:
                with open(os.path.join(self.text_dir, f"{version}.json"), "r", encoding="utf-8") as f:
                    self.data[version] = json.load(f)
            except Exception as e:
                log_error(f"[BibleDataLoader] Failed to load version '{version}': {e}")
                self.data[version] = {}
        return self.data[version]

    def get_books_for_version(self, version):
        """
        Returns the list of books available for the specified version.

        Args:
            version (str): Bible version key

        Returns:
            list: Book names in the version
        """
        verses = self.get_verses(version)
        return list(verses.keys()) if verses else []

    def _load_json(self, file_path):
        """
        Internal utility to safely load a JSON file.

        Args:
            file_path (str): Path to the JSON file

        Returns:
            dict: Parsed JSON content or empty dict on failure
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Warning] Failed to load {file_path}: {e}")
            return {}

    def get_standard_book(self, book_id: str, lang_code: str) -> str:
        """
        Returns localized canonical book name from internal ID.

        Args:
            book_id (str): Canonical book ID
            lang_code (str): Language code

        Returns:
            str: Localized name
        """
        return self.standard_book.get(book_id, {}).get(lang_code, book_id)

    def get_sort_key(self):
        """
        Returns a key function for sorting version names by region prefix.
        Required by GUI and CLI sorting logic. DO NOT DELETE.

        Returns:
            function: Sort key callable for use with sorted()
        """
        def sort_key(version_name: str):
            prefix = version_name.split()[0]
            return (self.sort_order.get(prefix, 99), version_name)
        return sort_key

    def load_version(self, version_key):
        """
        Manually loads a Bible version into memory.

        Args:
            version_key (str): Version file name without extension
        """
        path = os.path.join(self.text_dir, f"{version_key}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.data[version_key] = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load version {version_key}: {e}")
            self.data[version_key] = {}

    def extract_verses(self, versions, book, chapter, verse_range):
        """
        Extracts specific verses across multiple versions for given book/chapter/range.

        Args:
            versions (list): List of version keys
            book (str): Book name
            chapter (int): Chapter number
            verse_range (tuple): (start, end) range, or (start, -1) for full chapter

        Returns:
            dict: Nested verse dictionary grouped by version
        """
        results = {}
        chapter_str = str(chapter)
        start, end = verse_range

        for version in versions:
            verses = self.get_verses(version)
            book_data = verses.get(book, {})
            chapter_data = book_data.get(chapter_str, {})
            if not chapter_data:
                continue

            results.setdefault(version, {}).setdefault(book, {}).setdefault(chapter_str, {})

            # Full chapter case
            if end == -1:
                for verse_str, text in chapter_data.items():
                    if text:
                        results[version][book][chapter_str][verse_str] = text
            # Partial range case
            else:
                for i in range(start, end + 1):
                    verse_str = str(i)
                    text = chapter_data.get(verse_str)
                    if text:
                        results[version][book][chapter_str][verse_str] = text

        return results

    def get_verses_for_display(self, versions=None, book=None, chapter=None, verse_range=None):
        """
        Returns either extracted subset or full data depending on arguments.

        Args:
            versions (list): List of version keys
            book (str): Book name
            chapter (int): Chapter number
            verse_range (tuple): (start, end) range

        Returns:
            dict: Bible text in structured format
        """
        if versions and book and chapter and verse_range:
            return self.extract_verses(versions, book, chapter, verse_range)
        else:
            return self.get_verses()

    def get_book_alias(self, lang_code="ko") -> dict:
        """
        Returns book ID to alias mapping for display in selected language.

        Args:
            lang_code (str): Language code

        Returns:
            dict: book_id -> localized alias
        """
        return {
            book_id: data.get(lang_code, book_id)
            for book_id, data in self.standard_book.items()
        }

    def get_version_alias(self, lang_code="ko") -> dict:
        """
        Returns mapping of version keys to localized version aliases.

        Args:
            lang_code (str): Language code

        Returns:
            dict: version_key -> alias string
        """
        alias_map = {}
        for k, v in self.aliases_version.items():
            if isinstance(v, dict):
                alias_map[k] = v.get("aliases", {}).get(lang_code, k)
            else:
                alias_map[k] = v
        return alias_map