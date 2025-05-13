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

def handle_cli_metadata(args):
    """
    Handle CLI metadata options like --help, --version, and --about.

    Returns:
        bool: True if metadata was handled and command should exit.
    """
    if len(args) != 1:
        return False

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
        return True

    if args[0] in ("--version", "-v"):
        print(f"EuljiroBible v{APP_VERSION} (CLI interface)")
        return True

    if args[0] == "--about":
        print(f"EuljiroBible v{APP_VERSION} (CLI interface)")
        print("Based on: The Eulji-ro Presbyterian Church Bible App Project")
        print("Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin")
        print("Affiliated Church: The Eulji-ro Presbyterian Church")
        print("License: MIT License with Attribution Requirement (See LICENSE for more detail.)")
        return True

    return False

def handle_search_metadata(args):
    """
    Handle CLI metadata options for keyword search command.

    Args:
        args (list[str]): CLI args

    Returns:
        bool: True if metadata handled and program should exit.
    """
    if len(args) != 1:
        return False

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
        return True

    if args[0] in ("--version", "-v"):
        print(f"EuljiroBible v{APP_VERSION} (CLI interface)")
        return True

    if args[0] == "--about":
        print(f"EuljiroBible v{APP_VERSION} (CLI interface)")
        print("Based on: The Eulji-ro Presbyterian Church Bible App Project")
        print("Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin")
        print("Affiliated Church: The Eulji-ro Presbyterian Church")
        print("License: MIT License with Attribution Requirement (See LICENSE for more detail.)")
        return True

    return False

def show_usage_and_versions(cli_aliases):
    """
    Print general CLI usage and list of available version aliases.

    Args:
        cli_aliases (list[str]): List of CLI aliases to display.
    """
    print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Verse Lookup Tool")
    print("For more information, use: --about or --help\n")
    print("Usage: bible <version1> [version2 ...] <book> <chapter[:verse[-verse]]>\n")
    print("Available versions:")
    print(" ".join(cli_aliases))

def show_search_usage(cli_aliases):
    """
    Print usage information and available versions for keyword search command.

    Args:
        cli_aliases (list[str]): CLI version aliases
    """
    print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Keyword Search")
    print("For more information, use: --about or --help\n")
    print("Usage: bible search <version> <keyword1> [keyword2 ...]\n")
    print("Available versions:")
    print(" ".join(cli_aliases))

def load_cli_alias_map():
    """
    Load CLI alias map from JSON file.

    Returns:
        tuple: (alias_map, cli_aliases)
    """
    with open(alias_file, encoding="utf-8") as f:
        alias_map = json.load(f)
    cli_aliases = list(alias_map.values())
    return alias_map, cli_aliases

def parse_versions_from_args(args, alias_map):
    """
    Parse version aliases from CLI args.

    Args:
        args (list[str]): Raw CLI arguments.
        alias_map (dict): Full-to-short alias mapping.

    Returns:
        tuple: (versions, remaining_args)
    """
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

    # Remaining tokens are book and chapter/verse
    remaining_args = args[len(versions):]
    return versions, remaining_args

def resolve_search_version(version_alias, alias_map, keywords):
    """
    Resolve the full Bible version name for keyword search.

    Args:
        version_alias (str): CLI alias given by user
        alias_map (dict): Full-to-short alias map
        keywords (list[str]): User-specified search keywords

    Returns:
        str or None: Full version name if found; otherwise None
    """
    cli_aliases = set(alias_map.values())

    if version_alias not in cli_aliases:
        print(f"[ERROR] Unknown version: '{version_alias}'")
        return None

    if any(k in cli_aliases for k in keywords):
        print("[ERROR] Please specify only one version for keyword search.")
        return None

    matches = [k for k, v in alias_map.items() if v == version_alias]
    return matches[0] if matches else None

def parse_and_validate_reference(remaining):
    """
    Join and validate Bible reference tokens.

    Args:
        remaining (list[str]): List of tokens representing reference.

    Returns:
        tuple or None: (book, chapter, verse_range) if valid; otherwise None.
    """
    # Expecting: <book> <chapter[:verse[-verse]]>
    if len(remaining) != 2:
        print("[ERROR] Invalid input. Usage: bible <version1> [version2 ...] <book> <chapter[:verse[-verse]]>")
        return None

     # Parse Bible reference using shared parser
    raw_ref = " ".join(remaining)
    parsed = parse_reference(raw_ref)
    if not parsed:
        print("[ERROR] Invalid Bible reference format.")
        return None

    return parsed

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

def run_display_logic(versions, book, chapter, verse_range, alias_map):
    """
    Execute the main display logic for CLI output.

    Args:
        versions (list): Full version names.
        book (str): Resolved book name.
        chapter (int): Chapter number.
        verse_range (tuple): Start and optional end verse.
        alias_map (dict): CLI alias map.
    """
    bible_data = BibleDataLoader(json_dir=name_path, text_dir=data_path)
    for v in versions:
        bible_data.load_version(v)

    if book not in bible_data.get_verses(versions[0]):
        print(f"[ERROR] Unknown book name: '{book}'")
        return

    ref_func = lambda: (versions, book, chapter, verse_range, None)
    settings = {}

    def print_output(text):
        print(text)

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

    lang_code = detect_lang_code_from_aliases(versions, alias_map)
    if lang_code in {"he", "ar", "fa", "ur"}:
        print("")
        print("[Note] This is a Right-to-Left (RTL) language. CLI display may not be ideal.")

def run_keyword_search(full_version, keywords):
    """
    Run keyword search and print results.

    Args:
        full_version (str): Full Bible version name.
        keywords (list[str]): List of keywords to search.
    """
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

def handle_version_only(version, alias_map):
    """
    Handle the case where only the version is specified.

    Args:
        version (str): Full Bible version name.
        alias_map (dict): Full-to-short alias mapping.
    """
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

def handle_book_only(version, raw_book):
    """
    Handle the case where only a book name is given (show chapter count).

    Args:
        version (str): Full Bible version name.
        raw_book (str): User input book name.
    """
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
    if handle_cli_metadata(args):
        return

    alias_map, cli_aliases = load_cli_alias_map()

    if len(args) == 0:
        show_usage_and_versions(cli_aliases)
        return

    versions, remaining = parse_versions_from_args(args, alias_map)

    if len(remaining) == 0:
        handle_version_only(versions[0], alias_map)
        return

    if len(remaining) == 1:
        handle_book_only(versions[0], remaining[0])
        return

    parsed = parse_and_validate_reference(remaining)
    if not parsed:
        return

    book, chapter, verse_range = parsed

    run_display_logic(versions, book, chapter, verse_range, alias_map)

def run_search_command(args):
    """
    CLI keyword search command.

    Usage:
        bible search <version> <keyword1> [keyword2 ...]
    """

    if handle_search_metadata(args):
        return

    alias_map, cli_aliases = load_cli_alias_map()

    if len(args) < 2:
        show_search_usage(cli_aliases)
        return

    version_alias = args[0]
    keywords = args[1:]

    full_version = resolve_search_version(version_alias, alias_map, keywords)
    if not full_version:
        return

    run_keyword_search(full_version, keywords)