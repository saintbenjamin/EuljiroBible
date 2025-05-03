# -*- coding: utf-8 -*-
"""
File: gui/gui_main.py
GUI environment setup and main launcher logic for EuljiroBible.
Initializes QApplication, verifies environment, loads settings, and launches the main window.

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
import platform

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.config import paths
from core.store import storage
from core.utils.logger import log_debug
from core.version import APP_VERSION
from gui.launch import launch
from gui.config.config_manager import ConfigManager
from gui.constants import messages
from gui.utils.logger import handle_exception
from gui.utils.utils_env import setup_environment, verify_wsl_display
from gui.utils.ui_restore import restore_settings_to_ui
from gui.utils.utils_fonts import load_application_settings
from gui.utils.utils_save import save_user_settings
from gui.utils.utils_validation import verify_bible_data

def run_gui():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    log_debug('EuljiroBible started.')

    try:
        # Set up environment variables and fix WSL display if needed
        setup_environment()
        verify_wsl_display()

        # Create Qt application
        app = QApplication(sys.argv)
        if platform.system() == "Windows":
            app.setStyle("Fusion")  # Consistent look on Windows
        log_debug('QApplication initialized.')

        # Set application icon if available
        if os.path.exists(paths.ICON_FILE):
            app.setWindowIcon(QIcon(paths.ICON_FILE))

        # Load font and theme settings
        load_application_settings(app)

        # Check that Bible data is available and valid
        verify_bible_data()

        # Initialize version list and load user settings
        storage.VERSION_LIST.clear()
        version_list = []
        settings = ConfigManager.load()

        # Create and launch main window
        win = launch(app, version_list, settings, APP_VERSION)
        log_debug('WindowMain instance created.')

        # Restore saved UI settings (e.g. geometry, states)
        restore_settings_to_ui(win, settings)

        win.show()

        # Start Qt event loop
        exit_code = app.exec()

        # Persist user settings before exiting
        save_user_settings(app, win)

        sys.exit(exit_code)

    except Exception as e:
        # Handle any fatal error with GUI-safe dialog
        handle_exception(e, "Critical Error", messages.ERROR_MESSAGES["critical_error"])

def main():
    """
    Public GUI entry point.

    This function is called when gui_main.py is executed as the main script.
    """
    run_gui()

if __name__ == "__main__":
    main()