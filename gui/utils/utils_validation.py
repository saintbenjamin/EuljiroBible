# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/utils_validation.py
Validates presence of Bible data files necessary to launch the GUI properly.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import sys
import os
from PySide6.QtWidgets import QMessageBox

from core.config import paths
from gui.constants import messages

def verify_bible_data():
    """
    Verifies that Bible data directory and required JSON files exist.

    This function displays an error message and exits the app if the data directory or files are missing.
    """
    if not os.path.isdir(paths.BIBLE_DATA_DIR):
        msg = messages.ERROR_MESSAGES["bible_data_missing"].format(path=paths.BIBLE_DATA_DIR)
        QMessageBox.critical(None, "Error", msg)
        sys.exit(1)

    json_files = [f for f in os.listdir(paths.BIBLE_DATA_DIR) if f.endswith(".json")]
    if not json_files:
        msg = messages.ERROR_MESSAGES["bible_files_missing"].format(path=paths.BIBLE_DATA_DIR)
        QMessageBox.critical(None, "Error", msg)
        sys.exit(1)