# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/input_validators.py
Provides input validation utilities for form fields and user input processing.
Used to check integer values with optional range constraints.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

def validate_int(text, min_value=None, max_value=None):
    """
    Validates whether the given input text is a valid integer,
    optionally enforcing minimum and/or maximum bounds.

    Args:
        text (str): Input string to validate.
        min_value (int, optional): Lower bound (inclusive). Defaults to None.
        max_value (int, optional): Upper bound (inclusive). Defaults to None.

    Returns:
        tuple:
            - is_valid (bool): True if the input is a valid integer and within bounds.
            - value (int or None): The parsed integer if valid; otherwise None.

    Example:
        >>> validate_int("42", min_value=10, max_value=100)
        (True, 42)

        >>> validate_int("abc")
        (False, None)
    """
    try:
        # Attempt to convert text to integer
        value = int(text)

        # Check if below minimum bound
        if min_value is not None and value < min_value:
            return False, None

        # Check if above maximum bound
        if max_value is not None and value > max_value:
            return False, None

        return True, value

    except ValueError:
        # Conversion failed; not a valid integer
        return False, None