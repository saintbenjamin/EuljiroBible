# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/alias_loader.py
Loads Bible version alias mappings from a predefined JSON file.

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

def load_aliases():
    """
    Loads version alias mappings from aliases.json.

    Returns:
        dict: A dictionary mapping alias names to full Bible version names.

    Example:
        {
            "KJV": "King James Version",
            "NIV": "New International Version"
        }

    Warnings:
        Prints a warning message to stdout if loading fails, and returns an empty dict.
    """
    try:
        with open(paths.ALIASES_VERSION_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Warning] Failed to load aliases.json: {e}")
        return {}