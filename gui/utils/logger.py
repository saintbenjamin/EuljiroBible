# -*- coding: utf-8 -*-
"""
File: gui/utils/gui_logger.py
Provides GUI-specific logging helpers for EuljiroBible, including error dialog and log viewer.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import os
from PySide6.QtWidgets import (
    QMessageBox, QTextEdit, QVBoxLayout, QPushButton, QWidget
)
from core.utils.logger import log_error
from core.config import paths

def log_error_with_dialog(parent, exception: Exception, title="Error", extra_message=None):
    """
    Logs an error and shows a GUI message box to the user with an option to view the error log.

    Args:
        parent (QWidget): The parent widget for the QMessageBox.
        exception (Exception): The exception object to log and display.
        title (str): The title of the message box.
        extra_message (str, optional): Additional context to show in the message box.
    """
    log_error(exception)

    msg = str(exception)
    if extra_message:
        msg = f"{extra_message}\n\n{msg}"

    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)

    log_button = msg_box.addButton("View Error Log", QMessageBox.ActionRole)
    ok_button = msg_box.addButton("OK", QMessageBox.AcceptRole)

    msg_box.exec()

    try:
        # If user chooses to view error log, open MonitorErrorLog window
        if msg_box.clickedButton() == log_button:
            if parent is not None:
                parent.monitor_error_log = MonitorErrorLog(parent)
                parent.monitor_error_log.show()
                parent.monitor_error_log.raise_()
                parent.monitor_error_log.activateWindow()
            else:
                # Fallback in case no parent is provided
                global _monitor_error_log
                _monitor_error_log = MonitorErrorLog()
                _monitor_error_log.show()
                _monitor_error_log.raise_()
                _monitor_error_log.activateWindow()
    except Exception as e:
        log_error(e)

def handle_exception(exception, title="Error", user_message=None, parent=None):
    """
    Shortcut to log and show exception with dialog. Can be used globally in GUI.

    Args:
        exception (Exception): The exception to handle.
        title (str): Dialog title.
        user_message (str): Optional message for user context.
        parent (QWidget, optional): Parent widget.
    """
    log_error_with_dialog(parent, exception, title=title, extra_message=user_message)

class MonitorErrorLog(QWidget):
    """
    A window that displays the contents of the application error log file.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error Log")
        self.resize(700, 500)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        self.load_log()

    def load_log(self):
        """
        Loads and displays the error log content in the text edit field.
        """
        try:
            if os.path.exists(paths.LOG_FILE):
                with open(paths.LOG_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.text_edit.setPlainText(content)
        except Exception as e:
            log_error(e)