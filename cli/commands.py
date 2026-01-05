# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/cli/commands.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.


CLI command handlers for EuljiroBible.

This module contains the top-level command functions used by the CLI entry point:

- :func:`run_bible_command` for verse lookup and formatted verse output.
- :func:`run_search_command` for keyword search and result printing.

Design notes:

- Argument parsing here is intentionally lightweight. Deep validation and output
  formatting is delegated to shared core logic (e.g., :mod:`core.logic.verse_logic`).
- CLI error messages are expected to be English-only by project convention.
- Version names in the CLI are provided via a simplified alias map loaded from
  :data:`core.config.paths.ALIASES_VERSION_CLI_FILE`.

Limitations:

- CLI display for Right-to-Left (RTL) scripts (Hebrew/Arabic/etc.) depends on the
  terminal/font environment and may not render ideally. A note is printed when a
  likely RTL version is detected.
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
    Handle CLI metadata options for the verse lookup command.

    This function checks for single-token metadata options and prints an
    appropriate message. If a metadata option is handled, the caller should
    exit early without further parsing.

    Supported options:
        - ``--help`` / ``-h``: Print usage and examples.
        - ``--version`` / ``-v``: Print CLI version string.
        - ``--about``: Print author and license information.

    Args:
        args (list[str]): Raw CLI arguments *for the bible command* (excluding the script name).

    Returns:
        bool: ``True`` if a metadata option was handled and the command should exit,
        otherwise ``False``.
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
    Handle CLI metadata options for the keyword search command.

    Supported options:
        - ``--help`` / ``-h``: Print usage and examples.
        - ``--version`` / ``-v``: Print CLI version string.
        - ``--about``: Print author and license information.

    Args:
        args (list[str]): Raw CLI arguments for the ``search`` command.

    Returns:
        bool: ``True`` if a metadata option was handled and the command should exit,
        otherwise ``False``.
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
    Print general CLI usage for verse lookup and a list of available version aliases.

    Args:
        cli_aliases (list[str]): List of CLI aliases to display (e.g., ``["NKRV", "KJV"]``).

    Returns:
        None
    """
    print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Verse Lookup Tool")
    print("For more information, use: --about or --help\n")
    print("Usage: bible <version1> [version2 ...] <book> <chapter[:verse[-verse]]>\n")
    print("Available versions:")
    print(" ".join(cli_aliases))

def show_search_usage(cli_aliases):
    """
    Print usage for keyword search and a list of available version aliases.

    Args:
        cli_aliases (list[str]): CLI version aliases to display.

    Returns:
        None
    """
    print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Keyword Search")
    print("For more information, use: --about or --help\n")
    print("Usage: bible search <version> <keyword1> [keyword2 ...]\n")
    print("Available versions:")
    print(" ".join(cli_aliases))

def load_cli_alias_map():
    """
    Load the CLI alias map from the configured JSON file.

    The alias map is expected to be a JSON object mapping *full version names*
    to *CLI-friendly aliases* (strings). 
    
    Example shape::

        {
          "대한민국 개역개정 (1998)": "NKRV",
          "King James Version": "KJV"
        }

    Returns:
        tuple[dict, list[str]]: ``(alias_map, cli_aliases)`` where:

        - ``alias_map`` maps full version name -> CLI alias.
        - ``cli_aliases`` is a list of CLI aliases (values of the map).

    Raises:
        FileNotFoundError: If the alias file does not exist.
        json.JSONDecodeError: If the alias file is not valid JSON.
    """
    with open(alias_file, encoding="utf-8") as f:
        alias_map = json.load(f)
    cli_aliases = list(alias_map.values())
    return alias_map, cli_aliases

def parse_versions_from_args(args, alias_map):
    """
    Parse one or more version aliases from the beginning of CLI arguments.

    Parsing strategy:
        - Scan tokens left-to-right.
        - For each token, check if it matches any alias in ``alias_map.values()``.
        - Stop at the first token that does not match a known alias.
        - The remaining tokens are treated as the Bible reference portion.

    Args:
        args (list[str]): Raw CLI arguments.
        alias_map (dict): Full-to-short alias mapping (full version -> CLI alias).

    Returns:
        tuple[list[str], list[str]]: ``(versions, remaining_args)`` where:

        - ``versions`` is a list of full version names (keys from ``alias_map``).
        - ``remaining_args`` is the remainder of tokens after the version list.

    Note:
        - If no version tokens are found, ``versions`` will be an empty list.
        - Callers should validate and emit a helpful error.
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

    Keyword search requires exactly one version. This helper:

    - Validates that ``version_alias`` exists in the alias map.
    - Ensures none of the remaining keyword tokens look like a version alias.
    - Returns the full version name corresponding to ``version_alias``.

    Args:
        version_alias (str): CLI alias provided by the user.
        alias_map (dict): Full-to-short alias map (full version -> CLI alias).
        keywords (list[str]): User-supplied keyword tokens.

    Returns:
        str | None: Full version name if resolved; otherwise ``None`` (after printing an error).
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

    Expected token shape::

        <book> <chapter[:verse[-verse]]>

    This function joins the two tokens into a single reference string and uses
    :func:`core.utils.bible_parser.parse_reference` for parsing.

    Args:
        remaining (list[str]): Tokens representing the reference portion.

    Returns:
        tuple | None: ``(book, chapter, verse_range)`` if valid; otherwise ``None``.

    Side effects:
        Prints an ``[ERROR]`` message on invalid input.
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
    """
    Heuristically detect a language code based on selected versions.

    This is a CLI-only heuristic primarily used to warn about potential RTL rendering.
    The detection checks the lowercased version string (full canonical names in this
    module) against a small keyword list.

    Note:
        ``alias_map`` is currently unused, but kept for signature stability and
        potential future mapping to version metadata.

    Args:
        versions (list[str]): Full version names selected for output.
        alias_map (dict): Full-to-short alias mapping (reserved for future use).

    Returns:
        str: Language code among ``{"he", "ar", "fa", "ur", "ko"}``.
    """
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
    Execute the CLI verse display pipeline.

    This function:

    1) Loads the selected Bible versions.
    2) Validates that the requested book exists in the first version.
    3) Invokes :func:`core.logic.verse_logic.display_verse_logic` in CLI mode, sending output to stdout.

    Args:
        versions (list[str]): Full version names to load and display.
        book (str): Canonical book key expected by :class:`BibleDataLoader`.
        chapter (int): Chapter number.
        verse_range (tuple[int, int]): Verse range ``(start, end)``.
        alias_map (dict): Full-to-short alias mapping (for version aliases in output).

    Returns:
        None
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
    Run a keyword search and print results to stdout.

    This function loads the specified Bible version through
    :class:`core.utils.bible_keyword_searcher.BibleKeywordSearcher`, runs the search,
    prints each matching verse, then prints per-keyword frequencies and total count.

    Args:
        full_version (str): Full Bible version name.
        keywords (list[str]): Keywords to search (tokens). They are joined with spaces.

    Returns:
        None
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

    This prints the general usage plus the list of available books in that version.

    Args:
        version (str): Full Bible version name.
        alias_map (dict): Full-to-short alias mapping (full version -> CLI alias).

    Returns:
        None
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
    Handle the case where a version and book are provided, but no chapter/verse.

    This prints the chapter count for the requested book.

    Args:
        version (str): Full Bible version name.
        raw_book (str): User-supplied book token (may be localized/abbreviated).

    Returns:
        None
    """
    bible_data = BibleDataLoader(json_dir=name_path, text_dir=data_path)
    bible_data.load_version(version)

    # NOTE: resolve_book_name signature may depend on your parser implementation.
    # Here we preserve your current call shape and only document expectations.
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
    Entry point for the CLI ``bible`` command.

    Supported invocation patterns::

        $ bible                          # show usage and available versions
        $ bible NKRV                     # list books available in NKRV
        $ bible NKRV John                # show chapter count for John
        $ bible NKRV John 3:16           # show a single verse
        $ bible NKRV John 3:16-18        # show a verse range
        $ bible KJV NIV John 3:16        # show the same reference in multiple versions

    Behavior:

    - Handles metadata flags (``--help``, ``--version``, ``--about``).
    - Loads alias map and parses one or more version tokens from the front.
    - If only a version is given, prints available books.
    - If version + book are given, prints chapter count.
    - If a full reference is provided, prints formatted verse output via shared logic.

    Args:
        args (list[str]): Command-line arguments excluding the script name and excluding the ``bible`` token.

    Returns:
        None

    Note:
        - This function assumes at least one valid version alias is supplied when
        verse lookup is attempted. 
        - If no version is found, callers should see usage.
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
    Entry point for the CLI ``search`` command.

    Usage::

        bible search <version> <keyword1> [keyword2 ...]

    Examples::

        bible search NKRV 믿음
        bible search KJV faith grace

    Behavior:

    - Handles metadata flags (``--help``, ``--version``, ``--about``).
    - Requires exactly one version alias.
    - Runs keyword search and prints matches and keyword frequencies.

    Args:
        args (list[str]): Command-line arguments excluding the script name and excluding the ``search`` token.

    Returns:
        None
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