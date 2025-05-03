# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/utils_version.py
Provides utility to refresh and sort available Bible versions based on loaded metadata.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import os
from core.config import paths
from core.utils.bible_data_loader import BibleDataLoader
from core.utils.logger import log_error


def refresh_full_version_list():
    """
    Scans the Bible data directory for available versions, applies sort order, and returns the list.

    Returns:
        list[str]: Alphabetically or custom-ordered list of available Bible versions.

    Example:
        >>> refresh_full_version_list()
        ['KJV', 'NIV', 'NKRV', 'RSV']
    """
    loader = BibleDataLoader()

    try:
        # Collect .json files as version keys
        files = [f.replace(".json", "") for f in os.listdir(paths.BIBLE_DATA_DIR) if f.endswith(".json")]

        # Apply sorting based on your_sort_order.json from BibleDataLoader
        version_list = sorted(set(files), key=loader.get_sort_key())

        return version_list

    except Exception as e:
        # Log any unexpected error (e.g., folder access, invalid sort key)
        log_error(e)
        return []