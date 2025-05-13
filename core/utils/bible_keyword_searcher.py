# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/bible_keyword_searcher.py
Performs keyword-based search on Bible text files for EuljiroBible.

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
import re
from core.config import paths

class BibleKeywordSearcher:
    """
    Provides keyword search functionality for Bible verses.
    Searches the full text of the selected Bible version.
    """

    def __init__(self, version: str = "개역개정"):
        """
        Load Bible data for the given version.

        :param version: Bible version name (without .json)
        """
        self.version = version
        filepath = os.path.join(paths.BIBLE_DATA_DIR, f"{version}.json")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Bible data file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        with open(paths.STANDARD_BOOK_FILE, "r", encoding="utf-8") as f:
            self.name_map = json.load(f)

    def search_compact_string(self, keyword: str, limit: int = 100) -> list[dict]:
        """
        Search using compressed (whitespace-removed) keyword.
        Matches continuous strings regardless of spacing.
        """
        results = []
        stripped = keyword.strip()
        compressed = stripped.replace(" ", "")  # remove all spaces
        pattern = re.compile(re.escape(compressed), re.IGNORECASE)

        for book, chapters in self.data.items():
            for chapter_num, verses in chapters.items():
                for verse_num, verse_text in verses.items():
                    normalized = verse_text.replace(" ", "")
                    if compressed in normalized:
                        # Apply highlighting to the raw verse text
                        highlighted = pattern.sub(
                            lambda m: f'<span style="color:red; font-weight:bold;">{m.group(0)}</span>',
                            verse_text
                        )
                        results.append({
                            "book": book,
                            "chapter": int(chapter_num),
                            "verse": int(verse_num),
                            "text": verse_text.strip(),
                            "highlighted": highlighted.strip()
                        })

                        if len(results) >= limit:
                            return results
        return results

    def search_wordwise_and(self, keyword: str, limit: int = 100) -> list[dict]:
        """
        Search using word-based AND logic.
        All words must be present in the verse text.
        """
        results = []
        words = keyword.strip().split()
        regexes = [re.compile(re.escape(w), re.IGNORECASE) for w in words if w]

        for book, chapters in self.data.items():
            for ch_str, verses in chapters.items():
                for v_str, text in verses.items():
                    if all(r.search(text) for r in regexes):
                        # Apply highlight
                        highlighted = text
                        for r in regexes:
                            highlighted = r.sub(lambda m: f'<span style="color:red; font-weight:bold;">{m.group()}</span>', highlighted)
                        results.append({
                            "book": book,
                            "chapter": int(ch_str),
                            "verse": int(v_str),
                            "text": text,
                            "highlighted": highlighted
                        })
        return results
    
    def search(self, keyword: str, limit: int = 100, mode: str = "and") -> list[dict]:
        """
        Unified search interface.

        :param keyword: Input keyword(s)
        :param limit: Max results
        :param mode: 'and' (default) or 'compact'
        """
        if mode == "compact":
            return self.search_compact_string(keyword, limit)
        return self.search_wordwise_and(keyword, limit)

    def count_keywords(self, results: list[dict], keywords: list[str]) -> dict[str, int]:
        """
        Count total occurrences of each keyword across all result texts.

        This version performs full counting using regex (case-insensitive).

        :param results: List of verse dictionaries (search result)
        :param keywords: List of raw keywords to count
        :return: Dictionary mapping each keyword to count
        """
        counts = {w: 0 for w in keywords}
        for r in results:
            text = r["text"]
            for w in keywords:
                counts[w] += len(re.findall(re.escape(w), text, re.IGNORECASE))
        return counts