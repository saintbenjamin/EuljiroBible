# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/logger.py
Provides error and debug logging utilities for EuljiroBible.

Logs are written to a central file, only when needed.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import logging
import os

from core.config import paths

# Initialize logger
logger = logging.getLogger("EuljiroLogger")

# Avoid duplicate handlers (e.g., hot reload)
if not logger.hasHandlers():
    DEBUG_MODE = os.environ.get("DEBUG") == "1"
    logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.ERROR)

    # FileHandler is only added if error/debug logging occurs
    _file_handler = None

    def _ensure_file_handler():
        """
        Ensure that a file handler is attached to the logger.

        The file handler writes logs to the log file only when error or debug logging is required.
        """
        global _file_handler
        if _file_handler is None:
            _file_handler = logging.FileHandler(paths.LOG_FILE, encoding="utf-8")
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
            _file_handler.setFormatter(formatter)
            logger.addHandler(_file_handler)
else:
    DEBUG_MODE = logger.level == logging.DEBUG
    _file_handler = None

def log_error(e):
    """
    Logs an error with full traceback.

    The log file is only created if logging is actually used. This function captures the exception
    stack trace and logs it as an error message.

    :param e: The exception to log
    :type e: Exception
    """
    _ensure_file_handler()
    logger.error(str(e), exc_info=True)


def log_debug(msg):
    """
    Logs a debug message, only if DEBUG mode is enabled.

    :param msg: The message to log as a debug message
    :type msg: str
    """
    if DEBUG_MODE:
        _ensure_file_handler()
        logger.debug(msg)