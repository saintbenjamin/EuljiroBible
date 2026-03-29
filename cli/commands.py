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
- Available Bible versions are determined from the actual JSON files under
  ``data/``. Alias files are used only to improve display labels and optional
  CLI shorthand tokens.

Limitations:

- CLI display for Right-to-Left (RTL) scripts (Hebrew/Arabic/etc.) depends on the
  terminal/font environment and may not render ideally. A note is printed when a
  likely RTL version is detected.
"""

from core.config import paths
from core.version import APP_VERSION
from core.logic.verse_logic import display_verse_logic
from core.utils.bible_data_loader import BibleDataLoader
from core.utils.bible_parser import resolve_book_name, parse_reference
from core.utils.bible_keyword_searcher import BibleKeywordSearcher
from core.utils.utils_version import build_cli_version_catalog


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
        print("  bible search NKRV faith")
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


def _print_available_versions(version_catalog):
    """
    Print the list of Bible versions currently available to the CLI.

    The catalog is derived from the actual Bible JSON files under ``data/``.
    Each entry is printed using the best available user-facing label:

    - CLI alias from ``aliases_version_cli.json`` when available
    - GUI/display alias from ``aliases_version.json`` as a fallback
    - Raw version key (filename stem) if no alias metadata exists

    Args:
        version_catalog (list[dict]):
            Catalog rows produced by
            :func:`core.utils.utils_version.build_cli_version_catalog`.

    Returns:
        None
    """
    if not version_catalog:
        print("[none found]")
        return

    labels = []
    for entry in version_catalog:
        cli_label = entry["cli_label"]
        display_name = entry["display_name"]
        version_key = entry["version_key"]

        if cli_label == version_key == display_name:
            labels.append(cli_label)
        elif cli_label == version_key:
            labels.append(f"{cli_label} ({display_name})")
        elif display_name == version_key:
            labels.append(f"{cli_label} ({version_key})")
        else:
            labels.append(f"{cli_label} ({display_name})")

    print("; ".join(labels))


def show_usage_and_versions(version_catalog):
    """
    Print general CLI usage for verse lookup and the currently available versions.

    Args:
        version_catalog (list[dict]):
            Ordered catalog of versions that actually exist under ``data/``.

    Returns:
        None
    """
    print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Verse Lookup Tool")
    print("For more information, use: --about or --help\n")
    print("Usage: bible <version1> [version2 ...] <book> <chapter[:verse[-verse]]>\n")
    print("Available versions:")
    _print_available_versions(version_catalog)


def show_search_usage(version_catalog):
    """
    Print CLI usage for keyword search and the currently available versions.

    Args:
        version_catalog (list[dict]):
            Ordered catalog of versions that actually exist under ``data/``.

    Returns:
        None
    """
    print(f"EuljiroBible v{APP_VERSION} (CLI interface) - Bible Keyword Search")
    print("For more information, use: --about or --help\n")
    print("Usage: bible search <version> <keyword1> [keyword2 ...]\n")
    print("Available versions:")
    _print_available_versions(version_catalog)


def load_cli_version_catalog():
    """
    Build the CLI version catalog from the actual Bible data directory.

    This helper centralizes the CLI's notion of "available versions" so the
    CLI no longer depends on alias JSON files as the source of truth.
    Availability is determined by the presence of ``*.json`` files under
    ``data/``.

    Returns:
        tuple[list[dict], dict, dict]: ``(version_catalog, token_to_version, version_label_map)`` where:

        - ``version_catalog`` is an ordered list of version entries for display.
        - ``token_to_version`` maps accepted CLI input tokens to full version keys.
        - ``version_label_map`` maps full version keys to the preferred CLI label
          used in help text and formatted output.

    Note:
        Alias metadata is used only to improve labels and shorthand tokens.
        If alias metadata is missing, the raw version key remains usable.
    """
    return build_cli_version_catalog()


def parse_versions_from_args(args, token_to_version):
    """
    Parse one or more version tokens from the beginning of CLI arguments.

    Parsing strategy:
        - Scan tokens left-to-right.
        - For each token, check whether it matches a supported version token.
        - Stop at the first token that does not match a known version.
        - Treat the remaining tokens as the Bible reference portion.

    Args:
        args (list[str]): Raw CLI arguments.
        token_to_version (dict):
            Mapping of accepted CLI tokens to full version keys.

    Returns:
        tuple[list[str], list[str]]: ``(versions, remaining_args)`` where:

        - ``versions`` is a list of full version keys resolved from the input.
        - ``remaining_args`` is the remainder of tokens after version parsing.

    Note:
        - If no version tokens are found, ``versions`` will be an empty list.
        - Callers should validate that case and emit a helpful error.
    """
    versions = []
    for token in args:
        version = token_to_version.get(token)
        if version:
            versions.append(version)
        else:
            break

    remaining_args = args[len(versions):]
    return versions, remaining_args


def resolve_search_version(version_token, token_to_version, keywords):
    """
    Resolve the full Bible version key used for keyword search.

    Keyword search requires exactly one version. This helper:

    - Validates that ``version_token`` exists in the supported token map.
    - Ensures none of the remaining keyword tokens look like extra version tokens.
    - Returns the full version key corresponding to ``version_token``.

    Args:
        version_token (str):
            CLI token provided by the user.
        token_to_version (dict):
            Mapping of accepted CLI tokens to full version keys.
        keywords (list[str]):
            Remaining keyword tokens supplied by the user.

    Returns:
        str | None:
            Full version key if resolved; otherwise ``None`` (after printing an error).
    """
    cli_tokens = set(token_to_version.keys())

    if version_token not in cli_tokens:
        print(f"[ERROR] Unknown version: '{version_token}'")
        return None

    if any(keyword in cli_tokens for keyword in keywords):
        print("[ERROR] Please specify only one version for keyword search.")
        return None

    return token_to_version.get(version_token)


def parse_and_validate_reference(remaining):
    """
    Join and validate Bible reference tokens.

    Expected token shape::

        <book> <chapter[:verse[-verse]]>

    This function joins the remaining tokens into a single reference string and
    uses :func:`core.utils.bible_parser.parse_reference` for parsing.

    Args:
        remaining (list[str]):
            Tokens representing the reference portion.

    Returns:
        tuple | None:
            ``(book, chapter, verse_range)`` if valid; otherwise ``None``.

    Side effects:
        Prints an ``[ERROR]`` message on invalid input.
    """
    if len(remaining) != 2:
        print("[ERROR] Invalid input. Usage: bible <version1> [version2 ...] <book> <chapter[:verse[-verse]]>")
        return None

    raw_ref = " ".join(remaining)
    parsed = parse_reference(raw_ref)
    if not parsed:
        print("[ERROR] Invalid Bible reference format.")
        return None

    return parsed


def detect_lang_code_from_aliases(versions, _version_label_map):
    """
    Heuristically detect a language code based on selected versions.

    This is a CLI-only heuristic primarily used to warn about potential RTL
    rendering. Detection is based on keywords in the resolved version key.

    Note:
        ``_version_label_map`` is intentionally unused, but preserved for
        signature stability and possible future metadata-based detection.

    Args:
        versions (list[str]):
            Full version names selected for output.
        _version_label_map (dict):
            Reserved for future use.

    Returns:
        str:
            Language code among ``{"he", "ar", "fa", "ur", "ko"}``.
    """
    rtl_map = {
        "he": ["hebrew", "heb", "wlc", "mhb"],
        "ar": ["arabic", "svd"],
        "fa": ["persian", "fa", "farsi"],
        "ur": ["urdu", "ur"],
    }

    for version in versions:
        lower_name = version.lower()
        for code, keywords in rtl_map.items():
            if any(keyword in lower_name for keyword in keywords):
                return code

    return "ko"


def run_display_logic(versions, book, chapter, verse_range, version_label_map):
    """
    Execute the CLI verse display pipeline.

    This function:

    1) Loads the selected Bible versions.
    2) Validates that the requested book exists in the first version.
    3) Invokes :func:`core.logic.verse_logic.display_verse_logic` in CLI mode,
       sending formatted output to stdout.

    Args:
        versions (list[str]):
            Full version names to load and display.
        book (str):
            Canonical book key expected by :class:`BibleDataLoader`.
        chapter (int):
            Chapter number.
        verse_range (tuple[int, int]):
            Verse range ``(start, end)``.
        version_label_map (dict):
            Full version -> CLI label mapping used in formatted output.

    Returns:
        None
    """
    bible_data = BibleDataLoader(json_dir=name_path, text_dir=data_path)
    for version in versions:
        bible_data.load_version(version)

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
        version_alias=version_label_map,
        book_alias=None,
        is_cli=True,
    )

    lang_code = detect_lang_code_from_aliases(versions, version_label_map)
    if lang_code in {"he", "ar", "fa", "ur"}:
        print("")
        print("[Note] This is a Right-to-Left (RTL) language. CLI display may not be ideal.")


def run_keyword_search(full_version, keywords):
    """
    Run a keyword search and print results to stdout.

    This function loads the specified Bible version through
    :class:`core.utils.bible_keyword_searcher.BibleKeywordSearcher`, executes the
    search, prints each matching verse, then prints per-keyword frequencies and
    the total result count.

    Args:
        full_version (str):
            Full Bible version key.
        keywords (list[str]):
            Keywords to search. They are joined with spaces before searching.

    Returns:
        None
    """
    try:
        searcher = BibleKeywordSearcher(version=full_version)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return

    results = searcher.search(" ".join(keywords))
    counts = searcher.count_keywords(results, keywords)

    if not results:
        print("[INFO] No verses found.")
        return

    for result in results:
        print(f"[{result['book']} {result['chapter']}:{result['verse']}] {result['text']}")

    print("\nKeyword Frequencies:")
    for keyword, count in counts.items():
        print(f"{keyword}: {count}")

    print(f"\nResults: {len(results)} verses found.")


def handle_version_only(version, version_label_map):
    """
    Handle the case where only the version is specified.

    This prints the general usage plus the list of available books in that
    version.

    Args:
        version (str):
            Full Bible version key.
        version_label_map (dict):
            Full version -> CLI label mapping used for user-facing text.

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
        print(f"[INFO] Available books in {version_label_map.get(version, version)}:")
        print(" ".join(books))
    except Exception as exc:
        print(f"[ERROR] Failed to load version {version_label_map.get(version, version)}: {exc}")


def handle_book_only(version, raw_book):
    """
    Handle the case where a version and book are provided, but no chapter/verse.

    This prints the chapter count for the requested book.

    Args:
        version (str):
            Full Bible version key.
        raw_book (str):
            User-supplied book token (may be localized or abbreviated).

    Returns:
        None
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
    - Builds the CLI version catalog from actual Bible data files.
    - Parses one or more version tokens from the beginning of the argument list.
    - If only a version is given, prints available books.
    - If version + book are given, prints chapter count.
    - If a full reference is provided, prints formatted verse output via shared logic.

    Args:
        args (list[str]):
            Command-line arguments excluding the script name and excluding the
            ``bible`` token.

    Returns:
        None

    Note:
        - Version availability is determined by the actual contents of ``data/``.
        - Alias files affect labels and shorthand parsing only.
    """
    if handle_cli_metadata(args):
        return

    version_catalog, token_to_version, version_label_map = load_cli_version_catalog()

    if len(args) == 0:
        show_usage_and_versions(version_catalog)
        return

    versions, remaining = parse_versions_from_args(args, token_to_version)

    if not versions:
        print("[ERROR] Please specify at least one valid version.")
        show_usage_and_versions(version_catalog)
        return

    if len(remaining) == 0:
        handle_version_only(versions[0], version_label_map)
        return

    if len(remaining) == 1:
        handle_book_only(versions[0], remaining[0])
        return

    parsed = parse_and_validate_reference(remaining)
    if not parsed:
        return

    book, chapter, verse_range = parsed
    run_display_logic(versions, book, chapter, verse_range, version_label_map)


def run_search_command(args):
    """
    Entry point for the CLI ``search`` command.

    Usage::

        bible search <version> <keyword1> [keyword2 ...]

    Examples::

        bible search NKRV faith
        bible search KJV faith grace

    Behavior:

    - Handles metadata flags (``--help``, ``--version``, ``--about``).
    - Builds the CLI version catalog from actual Bible data files.
    - Requires exactly one version token.
    - Runs keyword search and prints matches and keyword frequencies.

    Args:
        args (list[str]):
            Command-line arguments excluding the script name and excluding the
            ``search`` token.

    Returns:
        None
    """
    if handle_search_metadata(args):
        return

    version_catalog, token_to_version, _ = load_cli_version_catalog()

    if len(args) < 2:
        show_search_usage(version_catalog)
        return

    version_token = args[0]
    keywords = args[1:]

    full_version = resolve_search_version(version_token, token_to_version, keywords)
    if not full_version:
        return

    run_keyword_search(full_version, keywords)
