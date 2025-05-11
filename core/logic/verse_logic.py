# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/logic/verse_logic.py

Provides core logic for verse reference parsing, formatting, and display.

This module is shared across GUI and CLI contexts. It encapsulates how verse ranges,
version compatibility, and formatting rules are handled throughout EuljiroBible.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from core.utils.utils_output import format_output
from core.utils.utils_bible import resolve_book_name

def parse_verse_range(verse_text, version, book, chapter, bible_data):
    """
    Parses a verse input string and returns a (start, end) tuple.

    Supports formats like "1", "3-5", or blank input (interpreted as full chapter).

    Args:
        verse_text (str): Raw input like "1", "4-6", or "".
        version (str): Bible version key.
        book (str): Internal book name key.
        chapter (int): Chapter number.
        bible_data (BibleDataLoader): Loader instance to resolve verse limits.

    Returns:
        tuple[int, int]: (start_verse, end_verse)

    Raises:
        ValueError: If the format is invalid or range is reversed.
    """
    verse_text = verse_text.strip()
    if not verse_text:
        # Empty input means: show entire chapter
        max_verse = bible_data.get_max_verse(version, book, chapter)
        return (1, max_verse), None

    if "-" in verse_text:
        try:
            start, end = verse_text.split("-", 1)
            start = int(start.strip())
            end = int(end.strip())
            if start > end:
                raise ValueError("invalid_verse_range")

            max_verse = bible_data.get_max_verse(version, book, chapter)
            if end > max_verse:
                return (start, max_verse), f"{book} {chapter}장은 {max_verse}절까지만 존재합니다. 입력된 범위를 조정했습니다."

            return (start, end), None
        except ValueError:
            raise ValueError("invalid_verse_format")
    else:
        try:
            verse = int(verse_text)
            return (verse, verse), None
        except ValueError:
            raise ValueError("invalid_verse_format")

def shift_verse_value(current_verse: int, delta: int, max_verse: int) -> int:
    """
    Computes a new verse number by applying delta with bounds.

    Args:
        current_verse (int): Current verse number.
        delta (int): +1, -1, etc.
        max_verse (int): Maximum valid verse in chapter.

    Returns:
        int: Adjusted verse number within valid range.
    """
    if current_verse + delta < 1:
        return 1
    elif current_verse + delta > max_verse:
        return max_verse
    return current_verse + delta


def resolve_reference(version_list, book_str, chapter_str, verse_str, bible_data, lang_code):
    """
    Resolves raw user input strings into normalized reference values.

    Args:
        version_list (list): List of Bible version keys.
        book_str (str): Raw book name (e.g., "요한복음").
        chapter_str (str): Raw chapter string (e.g., "3").
        verse_str (str): Raw verse string (e.g., "16-18").
        bible_data (BibleDataLoader): Data loader instance.
        lang_code (str): Language for book normalization.

    Returns:
        tuple: (versions, book_key, chapter:int, verse_range:(int,int))

    Raises:
        ValueError: If input is invalid.
    """
    versions = version_list
    book_key = resolve_book_name(book_str.strip(), bible_data, lang_code)
    if not book_key:
        raise ValueError("invalid_book")

    chapter = int(chapter_str.strip()) if chapter_str.strip().isdigit() else 1
    version = versions[0]

    try:
        verse_range, warning = parse_verse_range(verse_str.strip(), version, book_key, chapter, bible_data)
    except ValueError as e:
        raise e

    return versions, book_key, chapter, verse_range, warning


def get_common_books_among_versions(versions, get_verses_func, bible_data=None) -> list:
    """
    Returns list of books that are common to all selected versions.

    Canonical order is preserved if available.

    Args:
        versions (list): List of Bible versions.
        get_verses_func (function): Callable like bible_data.get_verses.
        bible_data (BibleDataLoader): For canonical book order.

    Returns:
        list[str]: List of book keys common to all versions.
    """
    book_sets = []
    for version in versions:
        books = bible_data.get_books_for_version(version)
        if books:
            book_sets.append(set(books))

    if not book_sets:
        return []

    common_books = set.intersection(*book_sets)
    canonical_order = list(bible_data.standard_book.keys())
    return [b for b in canonical_order if b in common_books]


def validate_versions_and_books(versions, bible_data=None) -> tuple:
    """
    Checks whether the versions are valid and share common books.

    Args:
        versions (list): List of selected versions.
        bible_data (BibleDataLoader): Data source.

    Returns:
        tuple: (validated_versions, common_books) or (None, None)
    """
    if not versions:
        return None, None

    common_books = get_common_books_among_versions(versions, bible_data.get_verses, bible_data)
    if not common_books:
        return versions, None

    return versions, common_books


def display_verse_logic(
    ref_func,
    output_target,
    bible_data,
    tr,
    settings,
    lang_code="ko",
    output_func=None,
    version_alias=None,
    book_alias=None,
    is_cli=False
):
    """
    Central function that handles fetching and displaying a verse block.

    Args:
        ref_func (callable): Function returning (versions, book, chapter, verse_range).
        output_target (QTextEdit or None): GUI output box (if applicable).
        bible_data (BibleDataLoader): Loaded Bible data.
        tr (function): Translation function.
        settings (dict): User settings.
        lang_code (str): Language code.
        output_func (callable): Optional stdout printer for CLI.
        version_alias (dict): Display-friendly version names.
        book_alias (dict): Display-friendly book names.
        is_cli (bool): True if running in CLI mode.

    Returns:
        str | None: Output string or error message printed.
    """
    try:
        versions, book, chapter, verse_range, warning = ref_func()

        if warning:
            if output_func:
                output_func("[경고] " + warning)
            elif hasattr(output_target, "append"):
                output_target.append("[경고] " + warning)

        if not versions:
            raise ValueError("error_no_version_selected")
        if not book:
            raise ValueError("invalid_book")

        if isinstance(verse_range, (int, str)):
            verse_range = (int(verse_range), int(verse_range))

        # Load verses depending on mode
        if is_cli:
            verses_dict = bible_data.get_verses_for_display(versions, book, chapter, verse_range)
        else:
            verses_dict = {v: bible_data.get_verses(v) for v in versions}

        # Resolve aliases if not provided
        book_alias = book_alias or bible_data.get_book_alias(lang_code)
        version_alias = version_alias or bible_data.get_version_alias(lang_code)

        formatted_output = format_output(
            versions, book, chapter, verse_range, verses_dict,
            tr, lang_code=lang_code,
            version_alias=version_alias,
            book_alias=book_alias,
            for_whitebox=False
        )

        if output_func:
            output_func(formatted_output)
        elif hasattr(output_target, "setPlainText"):
            output_target.setPlainText(formatted_output)
        else:
            print(formatted_output)

        return formatted_output

    except ValueError as e:
        msg_key = str(e)
        msg = {
            "invalid_verse_range": tr("warn_range_invalid_order"),
            "invalid_verse_input": tr("warn_verse_input_msg"),
            "invalid_verse_format": tr("warn_verse_format_msg"),
            "invalid_book": tr("warn_invalid_book"),
            "error_no_version_selected": tr("error_no_version_selected"),
        }.get(msg_key, tr("error_verse_input").format(msg_key))

        if output_func:
            output_func(msg)
        elif hasattr(output_target, "setPlainText"):
            output_target.setPlainText(msg)
        else:
            print(msg)

        return None

    except Exception as e:
        import traceback
        traceback.print_exc()

        try:
            msg_template = tr("error_verse_input") if callable(tr) else "error_verse_input"
            msg = msg_template.format(str(e)) if '{}' in msg_template else f"{msg_template}: {e}"
        except Exception:
            msg = f"[ERROR] {e}"

        if output_func:
            output_func(msg)
        elif hasattr(output_target, "setPlainText"):
            output_target.setPlainText(msg)
        else:
            print(msg)

        return None