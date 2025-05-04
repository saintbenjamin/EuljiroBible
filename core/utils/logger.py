# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/logger.py
Provides error and debug logging utilities for EuljiroBible.

Logs are written to a central file, only when needed.
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
    Creates the log file only if logging is actually used.
    """
    _ensure_file_handler()
    logger.error(str(e), exc_info=True)


def log_debug(msg):
    """
    Logs a debug message, only if DEBUG mode is enabled.
    """
    if DEBUG_MODE:
        _ensure_file_handler()
        logger.debug(msg)