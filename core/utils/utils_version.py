# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/core/utils/utils_version.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Provides utilities for working with available Bible versions.
"""

import json
from core.config import paths
from core.utils.bible_data_loader import BibleDataLoader
from core.utils.logger import log_error


def refresh_full_version_list():
    """
    Scans the Bible data directory for available versions, applies sort order, and returns the list.

    Example:
        >>> refresh_full_version_list()
        ['KJV', 'NIV', 'NKRV', 'RSV']

    Returns:
        list[str]: Alphabetically or custom-ordered list of available Bible versions.
    """
    loader = BibleDataLoader()

    try:
        return loader.get_available_versions()
    except Exception as e:
        # Log any unexpected error (e.g., folder access, invalid sort key)
        log_error(e)
        return []

def load_cli_alias_map():
    """
    Load the optional CLI alias map from the configured JSON file.

    The CLI alias map is a convenience layer only. It does not determine
    whether a Bible version is available; availability is determined from
    the actual files under ``data/``.

    Expected JSON shape::

        {
            "대한민국 개역개정 (1998)": "NKRV",
            "영어 King James Version (1611)": "KJV"
        }

    Returns:
        dict[str, str]:
            Mapping of ``version_key -> cli_token``.

    Note:
        Invalid, missing, or malformed files return an empty mapping so that the
        CLI can continue using raw version keys as fallback tokens.
    """
    try:
        with open(paths.ALIASES_VERSION_CLI_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}
    except Exception as e:
        log_error(e)
        return {}


def build_cli_version_catalog():
    """
    Build the CLI-facing version catalog from the actual data directory.

    Availability is determined strictly by ``data/*.json``. Alias files are used
    only to improve display labels and optional shorthand tokens.

    Returns:
        tuple[list[dict[str, str]], dict[str, str], dict[str, str]]:
            ``(entries, token_to_version, version_to_cli_label)`` where:

            - ``entries`` is an ordered list of catalog rows containing:
              ``version_key``, ``display_name``, and ``cli_label``.
            - ``token_to_version`` maps accepted CLI input tokens to version keys.
            - ``version_to_cli_label`` maps version keys to the label used in CLI
              output/help (CLI alias when present, otherwise the raw version key).

    Notes:
        - This function is the CLI-side source of truth for version availability.
        - ``aliases_version_cli.json`` and ``aliases_version.json`` are consulted
          only after the actual data file list has been collected.
        - The CLI accepts three token styles when available:
          explicit CLI alias, display alias, and raw version key.
    """
    loader = BibleDataLoader()
    version_keys = loader.get_available_versions()
    cli_alias_map = load_cli_alias_map()

    entries = []
    token_to_version = {}
    version_to_cli_label = {}

    for version_key in version_keys:
        display_name = loader.get_version_display_name(version_key)
        cli_label = cli_alias_map.get(version_key, version_key)

        entries.append({
            "version_key": version_key,
            "display_name": display_name,
            "cli_label": cli_label,
        })

        version_to_cli_label[version_key] = cli_label

        # Prefer explicit CLI aliases, but also allow the GUI/display alias and
        # the raw version key as fallback CLI tokens when they do not collide.
        token_to_version[cli_label] = version_key
        token_to_version.setdefault(display_name, version_key)
        token_to_version.setdefault(version_key, version_key)

    return entries, token_to_version, version_to_cli_label
