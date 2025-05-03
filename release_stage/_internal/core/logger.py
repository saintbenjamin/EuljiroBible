# -*- coding: utf-8 -*-
"""
File: EuljiroBible/core/utils/logger.py
Provides error and debug logging utilities for EuljiroBible.

Logs are written to a central file, with DEBUG mode controlled via environment variable `DEBUG`.
"""

import logging
import os
from core.config import paths

# Initialize logger for the application
logger = logging.getLogger("EuljiroLogger")

# Enable DEBUG logging only if environment variable DEBUG=1
DEBUG_MODE = os.environ.get("DEBUG") == "1"
logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.ERROR)

# Set up file handler to write logs to the designated file
file_handler = logging.FileHandler(paths.LOG_FILE, encoding="utf-8")
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)

# Avoid attaching duplicate handlers (e.g., during hot-reload in dev)
if not logger.hasHandlers():
    logger.addHandler(file_handler)


def log_error(e):
    """
    Logs an error with full traceback.

    Args:
        e (Exception): The exception object to log.
    """
    logger.error(str(e), exc_info=True)


def log_debug(msg):
    """
    Logs a debug message, only if DEBUG mode is enabled.

    Args:
        msg (str): Debug message to include in the log.
    """
    if DEBUG_MODE:
        logger.debug(msg)