# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/bible_parser.py
Parses Bible reference strings and resolves book name aliases from user input.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import re
import json

from core.config import paths

# ─────────────────────────────────────────────
# Load book name aliases from JSON at module load time
try:
    with open(paths.ALIASES_BOOK_FILE, encoding="utf-8") as f:
        BOOK_ALIASES = json.load(f)
except Exception as e:
    print(f"[!] Failed to load aliases_book.json: {e}")
    BOOK_ALIASES = {}
# ─────────────────────────────────────────────

def resolve_book_name(name: str, lang_map: dict = None, lang_code: str = "ko") -> str | None:
    """
    Resolve a user-provided book name (alias or standard) to the canonical internal ID.

    This version supports:
    - Strict alias matching from BOOK_ALIASES
    - Reverse matching for canonical names
    - Normalized comparison (lowercase, remove spaces/dots)
    - Optional fallback to standard_book name mapping if provided

    :param name: Raw book name from user input (e.g., "요삼", "1Jn", "Genesis")
    :param lang_map: Optional standard_book.json dict (key → { "ko": ..., "en": ... })
    :param lang_code: Language key for matching standard book names (default: "ko")
    :return: Canonical book ID (e.g., "3John"), or None if not found
    """
    if not name:
        return None

    raw = name.strip()
    normalized = raw.lower().replace(" ", "").replace(".", "")

    # 1. Try direct alias match (with normalization)
    for alias, canonical in BOOK_ALIASES.items():
        alias_norm = alias.strip().lower().replace(" ", "").replace(".", "")
        if normalized == alias_norm:
            return canonical

    # 2. Reverse match if name is already canonical
    for canonical in BOOK_ALIASES.values():
        if normalized == canonical.lower().replace(" ", "").replace(".", ""):
            return canonical

    # 3. Fallback: optional standard book name matching
    if lang_map:
        for key, names in lang_map.items():
            local = names.get(lang_code, "").lower().replace(" ", "").replace(".", "")
            en = names.get("en", "").lower().replace(" ", "").replace(".", "")
            if normalized == local or normalized == en:
                return key

    return None

def parse_reference(text: str):
    """
    Parse a Bible verse reference string into structured components.

    The expected input format is:
        "<book> <chapter>:<start_verse>-<end_verse>"
        Examples: "요 3" "요한복음 3:16", "John 3:14-16"

    :param text: The reference string entered by the user
    :return: Tuple of (book_id, chapter_number, list of verses) or None if invalid
    :rtype: tuple[str, int, list[int]] | None
    """
    text = text.strip()

    # Modified regex to also match "<book> <chapter>" (verse omitted)
    m = re.match(r"(.+?)\s*(\d+)(?::(\d+)(?:-(\d+))?)?", text)
    if not m:
        return None

    book_str, chapter_str, verse_start_str, verse_end_str = m.groups()

    # Resolve book name using alias map
    book_id = resolve_book_name(book_str)
    if not book_id:
        return None

    # Convert string components to integers
    chapter = int(chapter_str)

    # Support chapter-only input (e.g., "요한복음 3")
    if verse_start_str is None:
        return book_id, chapter, (1, -1)

    verse_start = int(verse_start_str)
    verse_end = int(verse_end_str) if verse_end_str else verse_start

    # Sanity check: verse range must be ascending
    if verse_end < verse_start:
        return None

    # Return all verses in range as tuple
    return book_id, chapter, (verse_start, verse_end)