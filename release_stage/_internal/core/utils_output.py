# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/utils_output.py
Provides functions for formatting Bible verses and saving them atomically
to output files for EuljiroBible. Handles both GUI and CLI output logic.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import os
import shutil
import time
import platform

from core.config import paths
from core.utils.logger import log_error


def format_output(
    versions,
    book,
    chapter,
    verse_range,
    verses_dict,
    tr,
    for_whitebox=False,
    lang_code="ko",
    bible_data=None,
    version_alias=None,
    book_alias=None
):
    """
    Formats Bible verses into a string for display or file output.
    Handles single/multiple versions, single verse or range, and appends metadata footer.

    Args:
        versions (list): Selected Bible versions.
        book (str): Canonical book key (e.g., "Genesis").
        chapter (int): Chapter number.
        verse_range (tuple): (start_verse, end_verse), (-1 for full chapter).
        verses_dict (dict): Nested verse dictionary structure.
        tr (function): Translation function (GUI: Qt tr, CLI: identity).
        for_whitebox (bool): Whether formatting is for overlay whitebox.
        lang_code (str): Language code (e.g., "ko", "en").
        bible_data (BibleDataLoader, optional): Optional Bible data access.
        version_alias (dict, optional): Version aliases mapping.
        book_alias (dict, optional): Book name alias mapping.

    Returns:
        str: Final formatted multi-line text.
    """
    lines = []

    # Resolve display name of the book
    display_book = book_alias.get(book, book) if isinstance(book_alias, dict) else book
    chapter_str = str(chapter)
    start_verse, end_verse = verse_range

    # Case: Single version & single verse
    if len(versions) == 1 and start_verse == end_verse:
        version = versions[0]
        verse_str = str(start_verse)
        text = verses_dict.get(version, {}).get(book, {}).get(chapter_str, {}).get(verse_str, tr("msg_no_word"))
        lines.append(text)

        display_verse = f"{chapter_str}:{verse_str}"
        version_label = version_alias.get(version, version) if version_alias else version
        footer = f"({display_book} {display_verse}, {version_label})"
        lines.append(footer)
        return "\n".join(lines)

    # Determine verse keys for iteration
    if end_verse == -1:
        verse_keys = sorted(
            verses_dict[versions[0]].get(book, {}).get(chapter_str, {}).keys(),
            key=lambda x: int(x)
        )
    else:
        verse_keys = [str(i) for i in range(start_verse, end_verse + 1)]

    # Append each verse with or without version separation
    for verse_str in verse_keys:
        for version in versions:
            text = verses_dict.get(version, {}).get(book, {}).get(chapter_str, {}).get(verse_str, tr("msg_no_word"))
            lines.append(f"{verse_str}  {text}")
        if len(versions) > 1:
            lines.append("")  # Add spacing between version blocks

    # Footer: e.g., (John 3장, KJV, NIV)
    version_footer = ", ".join(
        [version_alias.get(v, v) for v in versions] if version_alias else versions
    )
    chapter_label = f"{chapter}장" if lang_code == "ko" else chapter_str
    lines.append(f"({display_book} {chapter_label}, {version_footer})")

    return "\n".join(lines)


def atomic_write(path, content, retries=5, delay=0.5):
    """
    Atomically writes content to file using .tmp replacement pattern.
    Prevents data corruption and handles permission issues gracefully.

    Args:
        path (str): Output file path.
        content (str): Text content to write.
        retries (int): Retry attempts on failure (default 5).
        delay (float): Seconds between retries.

    Raises:
        Exception: Re-raised if final write attempt fails.
    """
    try:
        # Skip write if content hasn't changed
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = f.read()
            if existing == content:
                return

        tmp_path = path + ".tmp"

        # Write to temporary file first
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        # Preserve original file permissions
        if os.path.exists(path):
            shutil.copymode(path, tmp_path)

        # Attempt atomic replacement
        for attempt in range(retries):
            try:
                os.replace(tmp_path, path)
                return
            except PermissionError:
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise

    except Exception as e:
        log_error(e)
        raise


def resolve_output_path(settings, key="output_path"):
    """
    Resolves and validates output path from user settings.
    Ensures directory exists and avoids invalid platform-specific paths.

    Args:
        settings (dict): User/application settings.
        key (str): Settings key to read path from.

    Returns:
        str: Absolute, safe output path.
    """
    raw_path = settings.get(key)
    fallback_path = os.path.join(paths.BASE_DIR, "verse_output.txt")

    # Empty path fallback
    if not raw_path:
        settings[key] = fallback_path
        return fallback_path

    system = platform.system()

    # Windows: check drive existence
    if system == "Windows":
        drive_letter = os.path.splitdrive(raw_path)[0]
        if drive_letter and not os.path.exists(drive_letter + os.sep):
            print(f"[WARNING] Drive {drive_letter} not found. Falling back to project root.")
            settings[key] = fallback_path
            return fallback_path

    # Non-Windows: reject Windows-style paths
    if system != "Windows" and raw_path.lower().startswith("c:/"):
        print("[WARNING] Windows path detected on non-Windows system. Falling back.")
        settings[key] = fallback_path
        return fallback_path

    abs_path = os.path.abspath(raw_path)
    parent_dir = os.path.dirname(abs_path)

    # Ensure output directory exists
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    return abs_path


def save_to_files(merged, settings, parent=None):
    """
    Saves final merged text to disk using atomic write strategy.
    If saving fails, shows error dialog in GUI or logs in CLI.

    Args:
        merged (str): Final display text to save.
        settings (dict): Configuration containing output path.
        parent (QWidget, optional): For GUI error dialogs. Defaults to None.
    """
    output_path = resolve_output_path(settings)

    try:
        atomic_write(output_path, merged)
    except Exception as e:
        if parent:
            from PySide6.QtWidgets import QMessageBox
            rel_path = os.path.relpath(output_path, paths.BASE_DIR)
            QMessageBox.critical(
                parent,
                parent.tr("error_saving_title"),
                parent.tr("error_saving_msg_path").format(rel_path, e)
            )
        else:
            log_error(e)