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

    # def search(self, keyword: str, limit: int = 100) -> list[dict]:
    #     """
    #     Search Bible text for the given keyword.

    #     :param keyword: Keyword or phrase to search for
    #     :param limit: Maximum number of results to return
    #     :return: List of matching verse dictionaries
    #     """
    #     results = []
    #     keyword = keyword.strip().replace(" ", "")  # remove spaces for simple normalization

    #     for book, chapters in self.data.items():
    #         for chapter_num, verses in chapters.items():
    #             for verse_num, verse_text in verses.items():
    #                 normalized = verse_text.replace(" ", "")
    #                 if keyword in normalized:
    #                     results.append({
    #                         "book": book,
    #                         "chapter": int(chapter_num),
    #                         "verse": int(verse_num),
    #                         "text": verse_text.strip()
    #                     })
    #                     if len(results) >= limit:
    #                         return results
    #     return results

    def normalize(self, text):
        return re.sub(r"[^\w]", "", text)  # 특수기호 제거

    def search(self, keyword: str, limit: int = 100) -> list[dict]:
        results = []
        words = keyword.strip().split()
        words = [self.normalize(w) for w in words if w]

        for book, chapters in self.data.items():
            for chapter_num, verses in chapters.items():
                for verse_num, verse_text in verses.items():
                    norm_verse = self.normalize(verse_text)

                    if all(w in norm_verse for w in words):
                        results.append({
                            "book": self.get_korean_book_name(book),
                            "chapter": int(chapter_num),
                            "verse": int(verse_num),
                            "text": verse_text.strip()
                        })
                        if len(results) >= limit:
                            return results
        return results
    
    def get_korean_book_name(self, canonical_name):
        return self.name_map.get(canonical_name, {}).get("ko", canonical_name)
    
    def count_keywords(self, results: list[dict], keywords: list[str]) -> dict[str, int]:
        """
        Count how many times each keyword appears across the search results.

        :param results: List of verse dictionaries (search result)
        :param keywords: Original list of keywords
        :return: Dictionary mapping each keyword to its count
        """
        counts = {k: 0 for k in keywords}
        for item in results:
            text = self.normalize(item["text"])
            for k in keywords:
                if self.normalize(k) in text:
                    counts[k] += 1
        return counts