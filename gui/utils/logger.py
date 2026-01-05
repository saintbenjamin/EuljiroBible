# -*- coding: utf-8 -*-
"""
:File: gui/utils/gui_logger.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Provides GUI-specific logging helpers for EuljiroBible, including error dialog and log viewer.
"""

import os
from PySide6.QtWidgets import (
    QMessageBox, QTextEdit, QVBoxLayout, QPushButton, QWidget
)
from core.utils.logger import log_error
from core.config import paths

def log_error_with_dialog(parent, exception: Exception, title="Error", extra_message=None):
    """
    Log an exception and show a critical dialog with an optional "View Error Log" action.

    This helper is intended for GUI-safe error reporting:

    - Always writes the exception to the application error log via `log_error()`.
    - Shows a QMessageBox with the error text (and optional extra context).
    - If the user selects "View Error Log", opens a `MonitorErrorLog` window.

    Args:
        parent (QWidget | None): Parent widget for the QMessageBox and log viewer window.
            If None, a standalone log viewer window is created.
        exception (Exception): The exception instance to log and present to the user.
        title (str): Dialog window title.
        extra_message (str | None): Optional context string shown above the exception message.
            Use this to explain what the app was trying to do when the error occurred.

    Returns:
        None
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
    Handle an exception by logging it and showing a GUI dialog.

    This is a convenience wrapper around `log_error_with_dialog()` for use across the GUI.
    Use this when you want a single call site that:

    - logs the exception
    - displays a user-facing message (optional)
    - keeps consistent dialog titles

    Args:
        exception (Exception): The exception instance to handle.
        title (str): Dialog window title.
        user_message (str | None): Optional, user-friendly context message shown in the dialog.
        parent (QWidget | None): Parent widget for the dialog (and log viewer if opened).

    Returns:
        None
    """
    log_error_with_dialog(parent, exception, title=title, extra_message=user_message)

class MonitorErrorLog(QWidget):
    """
    GUI window that displays the contents of the application's error log file.

    This viewer is used by error dialogs to let the user inspect `paths.LOG_FILE`
    without leaving the application. It renders the full file into a read-only QTextEdit.

    Attributes:
        text_edit (QTextEdit): Read-only text area showing the error log content.
        close_button (QPushButton): Button to close the window.
    """

    def __init__(self, parent=None):
        """
        Initialize the error log viewer window and load current log contents.

        Args:
            parent (QWidget | None): Optional parent widget.

        Returns:
            None
        """
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
        Load `paths.LOG_FILE` and display its contents in the viewer text area.

        Behavior:
        - If the log file does not exist, the viewer stays empty.
        - Any read failure is logged via `log_error()` (no dialog recursion).

        Returns:
            None
        """
        try:
            if os.path.exists(paths.LOG_FILE):
                with open(paths.LOG_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.text_edit.setPlainText(content)
        except Exception as e:
            log_error(e)