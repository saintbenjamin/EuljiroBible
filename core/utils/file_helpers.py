# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/file_helpers.py
Provides utility functions for evaluating file-based overlay display conditions.
Primarily used to determine whether the verse output file contains valid content
that warrants triggering the overlay display.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import os

def should_show_overlay(file_path):
    """
    Determines whether the overlay should be shown based on the content
    of the specified verse output file.

    The overlay should only be displayed if:
    - The file exists, and
    - The file contains non-empty text (ignoring whitespace).

    Args:
        file_path (str): Absolute or relative path to the verse output file.

    Returns:
        bool: True if overlay should be shown, False otherwise.
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return False

    try:
        # Attempt to read and trim whitespace
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Return True if non-empty, False otherwise
        return bool(content)
    except Exception:
        # On read failure or encoding issue, default to not showing
        return False