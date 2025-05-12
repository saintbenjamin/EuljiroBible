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

    # [Benji] This is AND search algorithm.

    # def search(self, keyword: str, limit: int = 100) -> list[dict]:
    #     """
    #     Search Bible text for the given keyword (simple normalized OR-search).

    #     :param keyword: Keyword or phrase to search for
    #     :param limit: Maximum number of results to return
    #     :return: List of matching verse dictionaries
    #     """
    #     results = []
    #     stripped = keyword.strip()
    #     compressed = stripped.replace(" ", "")  # remove all spaces
    #     pattern = re.compile(re.escape(compressed), re.IGNORECASE)

    #     for book, chapters in self.data.items():
    #         for chapter_num, verses in chapters.items():
    #             for verse_num, verse_text in verses.items():
    #                 normalized = verse_text.replace(" ", "")
    #                 if compressed in normalized:
    #                     # Apply highlighting to the raw verse text
    #                     highlighted = pattern.sub(
    #                         lambda m: f'<span style="color:red; font-weight:bold;">{m.group(0)}</span>',
    #                         verse_text
    #                     )
    #                     results.append({
    #                         "book": book,
    #                         "chapter": int(chapter_num),
    #                         "verse": int(verse_num),
    #                         "text": verse_text.strip(),
    #                         "highlighted": highlighted.strip()
    #                     })

    #                     if len(results) >= limit:
    #                         return results
    #     return results

    # [Benji] These two (normalize, search) are for OR search algorithm.

    def normalize(self, text):
        """
        Normalize the given text by removing all non-word characters.

        This function strips out all special characters including punctuation and whitespace,
        leaving only alphanumeric and underscore characters. Used for keyword comparison.

        :param text: Input string to normalize
        :type text: str
        :return: Normalized string with non-word characters removed
        :rtype: str
        """
        return re.sub(r"[^\w]", "", text)

    def search(self, keyword: str, limit: int = 100) -> list[dict]:
        """
        Search Bible text for the given keyword.

        :param keyword: Keyword or phrase to search for
        :param limit: Maximum number of results to return
        :return: List of matching verse dictionaries
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

    def get_korean_book_name(self, canonical_name):
        """
        Retrieve the Korean display name for the given canonical book ID.

        :param canonical_name: Internal Bible book ID (e.g., "Genesis", "John")
        :type canonical_name: str
        :return: Korean book name if found, otherwise the input name
        :rtype: str
        """
        return self.name_map.get(canonical_name, {}).get("ko", canonical_name)
    
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
