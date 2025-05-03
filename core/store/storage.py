# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/store/storage.py
Centralized global storage for Bible data and version management in EuljiroBible.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

# ================================
# Global Bible Data Store
# ================================
# This module provides centralized in-memory storage containers to be used across
# the application for Bible data handling and version management. The data is loaded
# and modified via BibleDataLoader or relevant core modules.

bible_map = {}
"""
dict: Loaded Bible text content for each version.

Structure:
    {
        "<Version Name>": {
            "<Book Name>": {
                "<Chapter Number>": {
                    "<Verse Number>": "Text"
                }
            }
        }
    }

Example:
    bible_map["NIV"]["John"]["3"]["16"] => "For God so loved the world..."
"""

loaded_versions = []
"""
list: Version names that are currently loaded into memory.

Used to prevent reloading the same data multiple times.
"""

VERSIONS = {}
"""
dict: Shortcut dictionary pointing to data of currently selected Bible versions.

Typically a subset of `bible_map`, populated according to VERSION_LIST.
"""

VERSION_LIST = []
"""
list: Currently selected Bible versions for verse display or lookup.
"""

FULL_VERSION_LIST = []
"""
list: All available Bible versions found on disk and recognized as valid.

This is typically populated at startup by scanning the bible JSON directory.
"""