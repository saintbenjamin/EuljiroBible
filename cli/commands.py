# -*- coding: utf-8 -*-
"""
File: EuljiroBible/cli/commands.py

CLI command handler for EuljiroBible.

Parses command-line arguments and coordinates verse lookup and display.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import json
from core.config import paths
from core.version import APP_VERSION
from core.logic.verse_logic import display_verse_logic
from core.utils.bible_data_loader import BibleDataLoader
from core.utils.bible_parser import resolve_book_name, parse_reference
from core.utils.bible_keyword_searcher import BibleKeywordSearcher

# Paths to alias and data files
alias_file = paths.ALIASES_VERSION_CLI_FILE
name_path = paths.BIBLE_NAME_DIR
data_path = paths.BIBLE_DATA_DIR


def run_bible_command(args):
    """
    Main CLI handler for parsing and executing Bible verse search commands.

    Args:
        args (list[str]): Command-line arguments excluding the script name.

    Examples:
        $ bible NKRV John 3:16
        $ bible NKRV NIV John 3
        $ bible NKRV

    Behavior:
        - Prints usage/help if no args.
        - Lists books if only version and book given.
        - Shows verse(s) if full reference is given.
    """
    # --- CLI metadata options ---
    if len(args) == 1:
        if args[0] in ("--help", "-h"):
            print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Verse Lookup Tool\n")
            print("Usage:")
            print("  bible <version1> [version2 ...] <book> <chapter[:verse[-verse]]>\n")
            print("Examples:")
            print("  bible NKRV John 3:16")
            print("  bible KJV NIV Genesis 1:1-3\n")
            print("Options:")
            print("  --help       Show this help message and exit")
            print("  --version    Show CLI version and exit")
            print("  --about      Show author and license information\n")
            return

        if args[0] in ("--version", "-v"):
            print(f"EuljiroBible v{APP_VERSION} (CLI interface)")
            return

        if args[0] == "--about":
            print(f"EuljiroBible v{APP_VERSION} (CLI interface)")
            print("Based on: The Eulji-ro Presbyterian Church Bible App Project")
            print("Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin")
            print("Affiliated Church: The Eulji-ro Presbyterian Church")
            print("License: MIT License with Attribution Requirement (See LICENSE for more detail.)")
            return
    with open(alias_file, encoding="utf-8") as f:
        alias_map = json.load(f)

    cli_aliases = list(alias_map.values())

    if len(args) == 0:
        print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Verse Lookup Tool")
        print("For more information, use: --about or --help\n")
        print("Usage: bible <version1> [version2 ...] <book> <chapter[:verse[-verse]]>\n")
        print("Available versions:")
        print(" ".join(cli_aliases))
        return

    # Parse versions from args
    versions = []
    for token in args:
        found = False
        for full, short in alias_map.items():
            if token == short:
                versions.append(full)
                found = True
                break
        if not found:
            break

    if not versions:
        print("[ERROR] No valid versions found.")
        return

    # Remaining tokens are book and chapter/verse
    remaining = args[len(versions):]

    # If only version(s) provided, list available books
    if len(remaining) == 0:
        version = versions[0]
        bible_data = BibleDataLoader(json_dir=name_path, text_dir=data_path)
        try:
            bible_data.load_version(version)
            books = list(bible_data.get_verses(version).keys())
            print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Verse Lookup Tool\n")
            print("Usage:")
            print("  bible <version1> [version2 ...] <book> <chapter[:verse[-verse]]>\n")
            print(f"[INFO] Available books in {alias_map[version]}:")
            print(" ".join(books))
        except Exception as e:
            print(f"[ERROR] Failed to load version {alias_map[version]}: {e}")
        return

    # If only book is given, show chapter count
    if len(remaining) == 1:
        version = versions[0]
        raw_book = remaining[0]
        bible_data = BibleDataLoader(json_dir=name_path, text_dir=data_path)
        bible_data.load_version(version)
        book = resolve_book_name(raw_book)
        if not book or book not in bible_data.get_verses(version):
            print(f"[ERROR] Unknown book name: '{raw_book}'")
            return
        chapter_count = len(bible_data.get_verses(version)[book])
        print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Verse Lookup Tool\n")
        print("Usage:")
        print("  bible <version1> [version2 ...] <book> <chapter[:verse[-verse]]>\n")
        print(f"[INFO] The Book of {raw_book} has {chapter_count} chapters.")
        return

    # Expecting: <book> <chapter[:verse[-verse]]>
    if len(remaining) != 2:
        print("[ERROR] Invalid input. Usage: bible <version1> [version2 ...] <book> <chapter[:verse[-verse]]>")
        return

    # Parse Bible reference using shared parser
    raw_ref = " ".join(remaining)
    parsed = parse_reference(raw_ref)
    if not parsed:
        print("[ERROR] Invalid Bible reference format.")
        return

    book, chapter, verse_range = parsed

    bible_data = BibleDataLoader(json_dir=name_path, text_dir=data_path)
    for v in versions:
        bible_data.load_version(v)

    # Check book validity in loaded version
    if book not in bible_data.get_verses(versions[0]):
        print(f"[ERROR] Unknown book name: '{book}'")
        return

    ref_func = lambda: (versions, book, chapter, verse_range, None)
    settings = {}

    def print_output(text):
        print(text)

    # Execute core logic and print output
    display_verse_logic(
        ref_func,
        None,
        bible_data,
        lambda x: x,
        settings,
        lang_code="ko",
        output_func=print_output,
        version_alias=alias_map,
        book_alias=None,
        is_cli=True
    )

    def detect_lang_code_from_aliases(versions, alias_map):
        rtl_map = {
            "he": ["히브리어", "hebrew", "heb", "wlc", "mhb"],
            "ar": ["아랍어", "arabic", "ar", "svd"],
            "fa": ["페르시아어", "persian", "fa", "farsi"],
            "ur": ["우르두어", "urdu", "ur"]
        }

        for version in versions:
            alias = version.lower()
            for code, keywords in rtl_map.items():
                if any(keyword in alias for keyword in keywords):
                    return code

        return "ko"

    lang_code = detect_lang_code_from_aliases(versions, alias_map)

    rtl_languages = {"he", "ar", "fa", "ur"}
    if lang_code in rtl_languages:
        print("")
        print("[Note] This is a Right-to-Left (RTL) language. CLI display may not be ideal.")

def run_search_command(args):
    """
    CLI keyword search command.

    Usage:
        bible search <version> <keyword1> [keyword2 ...]
    """

    # --- CLI metadata options for bible search ---
    if len(args) == 1:
        if args[0] in ("--help", "-h"):
            print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Keyword Search\n")
            print("Usage:")
            print("  bible search <version> <keyword1> [keyword2 ...]\n")
            print("Examples:")
            print("  bible search NKRV 믿음")
            print("  bible search KJV faith grace\n")
            print("Options:")
            print("  --help       Show this help message and exit")
            print("  --version    Show CLI version and exit")
            print("  --about      Show author and license information\n")
            return

        if args[0] in ("--version", "-v"):
            print(f"EuljiroBible v{APP_VERSION} (CLI interface)")
            return

        if args[0] == "--about":
            print(f"EuljiroBible v{APP_VERSION} (CLI interface)")
            print("Based on: The Eulji-ro Presbyterian Church Bible App Project")
            print("Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin")
            print("Affiliated Church: The Eulji-ro Presbyterian Church")
            print("License: MIT License with Attribution Requirement (See LICENSE for more detail.)")
            return

    with open(alias_file, encoding="utf-8") as f:
        alias_map = json.load(f)

    cli_aliases = list(alias_map.values())

    if len(args) < 2:
        print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Keyword Search")
        print("For more information, use: --about or --help\n")
        print("Usage: bible search <version> <keyword1> [keyword2 ...]\n")
        print("Available versions:")
        print(" ".join(cli_aliases))
        return

    version_alias = args[0]
    keywords = args[1:]

    if version_alias not in cli_aliases:
        print(f"[ERROR] Unknown version: '{version_alias}'")
        return

    if any(k in cli_aliases for k in keywords):
        print("[ERROR] Please specify only one version for keyword search.")
        return

    # Resolve full version name from alias
    full_version = [k for k, v in alias_map.items() if v == version_alias][0]

    # Load data
    try:
        searcher = BibleKeywordSearcher(version=full_version)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return

    results = searcher.search(" ".join(keywords))
    counts = searcher.count_keywords(results, keywords)

    if not results:
        print("[INFO] No verses found.")
        return

    for res in results:
        print(f"[{res['book']} {res['chapter']}:{res['verse']}] {res['text']}")

    print("\nKeyword Frequencies:")
    for k, v in counts.items():
        print(f"{k}: {v}")

    print(f"\nResults: {len(results)} verses found.")