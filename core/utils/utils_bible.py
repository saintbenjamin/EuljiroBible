# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/utils_bible.py
Provides Bible-related utility functions for EuljiroBible, such as:
- Resolving localized book names
- Loading Bible data from JSON
- Searching keywords with highlighting
- Normalizing and displaying book names

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import re
from core.utils.bible_data_loader import BibleDataLoader

def resolve_book_name(book_str: str, bible_data: BibleDataLoader, lang_code: str) -> str | None:
    """
    Resolves user input (abbreviated or alias form) to canonical book ID.

    Args:
        book_str (str): Input like "요삼", "1Jn", "Revelation"
        bible_data (BibleDataLoader): Loader with alias mappings
        lang_code (str): Language code (unused in flat alias dict)

    Returns:
        str or None: Canonical English book ID (e.g. "3 John"), or None if not found
    """
    if not book_str:
        return None

    query = book_str.strip().lower().replace(" ", "").replace(".", "")

    # 1. Flat alias match (e.g., "요삼" → "3John")
    for alias, canonical in bible_data.aliases_book.items():
        alias_norm = alias.strip().lower().replace(" ", "").replace(".", "")
        if query == alias_norm:
            return canonical

    # 2. Fallback to standard_book name match (just in case)
    for key, names in bible_data.standard_book.items():
        name_local = names.get(lang_code, "").strip().lower().replace(" ", "")
        name_en = names.get("en", "").strip().lower().replace(" ", "")
        if query == name_local or query == name_en:
            return key

    return None

def normalize_book_name(book_text, bible_data, lang_code="ko"):
    """
    Converts a localized book name to its canonical English key.

    Args:
        book_text (str): Localized book name, e.g., "창세기"
        bible_data (BibleDataLoader)
        lang_code (str): Language code, default "ko"

    Returns:
        str: Canonical book key, e.g., "Genesis"
    """
    for eng_key, names in bible_data.standard_book.items():
        if names.get(lang_code, "").strip() == book_text.strip():
            return eng_key
    return book_text

def search_keywords(bible_data: BibleDataLoader, version: str, keywords: list[str]) -> list[dict]:
    """
    Searches verses that contain all specified keywords.

    Args:
        bible_data (BibleDataLoader): Instance with loaded data
        version (str): Bible version key
        keywords (list[str]): List of keywords to search

    Returns:
        list[dict]: Matching verses with highlight metadata
    """
    if not version or not keywords:
        return []

    data = bible_data.get_verses(version)
    if not data:
        return []

    regexes = [re.compile(re.escape(w), re.IGNORECASE) for w in keywords]
    results = []

    for book, chapters in data.items():
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


def keyword_counts(results, keywords):
    """
    Counts occurrences of each keyword in the search results.

    Args:
        results (list[dict]): Result list from search_keywords()
        keywords (list[str]): List of keywords to count

    Returns:
        dict: keyword -> count
    """
    counts = {w: 0 for w in keywords}
    for r in results:
        text = r["text"]
        for w in keywords:
            counts[w] += len(re.findall(re.escape(w), text, re.IGNORECASE))
    return counts


def compact_book_id(name: str) -> str:
    """
    Normalizes a book name by removing all whitespace.

    Args:
        name (str): Raw book string (e.g. "1 John")

    Returns:
        str: Compact ID (e.g. "1John")
    """
    return re.sub(r"\s+", "", name)