# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/ui/monitor_memory.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Popup window for monitoring the current Python process memory usage.

This module provides a lightweight GUI tool that periodically measures the
resident set size (RSS) of the running process, appends the record to a log file,
and displays the latest values in real time.

Key behaviors:

- Memory is sampled at a user-configurable interval (seconds).
- Each sample is appended to ``paths.MEMORY_LOG_FILE`` (typically ``memory_log.txt``).
- Entries exceeding a fixed warning threshold (currently 400 MB) are highlighted in the UI and marked as warnings in the log output.

Note:
- This tool is intended for runtime debugging and stability monitoring.
- The monitor does not attempt to manage or reduce memory; it only reports.
"""

import psutil, os
from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit, QLabel
from PySide6.QtCore import QTimer
from PySide6.QtGui import QTextCursor, QTextCharFormat, QColor

from core.config import paths
from gui.config.config_manager import ConfigManager

class MonitorMemory(QWidget):
    """
    Popup ``QWidget`` that monitors and displays the current process memory usage.

    The widget periodically reads RSS memory usage using ``psutil`` and:

    - Appends log lines to ``paths.MEMORY_LOG_FILE``.
    - Displays the log in a read-only ``QTextEdit`` in real time.
    - Highlights entries in red when the warning threshold is exceeded.

    Attributes:
        interval_input (QLineEdit):
            Text input containing the monitoring interval in seconds.

        save_btn (QPushButton):
            Button that saves the interval to settings and applies it immediately.

        text_area (QTextEdit):
            Read-only area showing the rolling log output (styled by warning level).

        close_btn (QPushButton):
            Button that stops monitoring and closes the window.

        timer (QTimer):
            Periodic timer that triggers memory sampling.

        interval_sec (int):
            Effective monitoring interval in seconds (clamped to at least 1).
    """

    def __init__(self, interval_sec=5, parent=None):
        """
        Initialize the memory monitor widget and build the UI.

        Args:
            interval_sec (int):
                Initial monitoring interval in seconds. Values less than 1 are clamped
                to 1 when applied.

            parent (QWidget, optional):
                Optional parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Memory Monitor")
        self.resize(520, 430)

        # Interval control row
        self.interval_input = QLineEdit(str(interval_sec))
        self.interval_input.setFixedWidth(50)
        self.save_btn = QPushButton("저장")
        self.save_btn.clicked.connect(self.save_interval)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("체크 간격 (초):"))
        interval_layout.addWidget(self.interval_input)
        interval_layout.addWidget(self.save_btn)

        # Output area for memory log
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        # Close button
        self.close_btn = QPushButton("닫기")
        self.close_btn.clicked.connect(self.close_monitor)

        layout = QVBoxLayout()
        layout.addLayout(interval_layout)
        layout.addWidget(self.text_area)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)

        # Memory monitoring timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.record_and_display_memory)

        self.set_interval(interval_sec)
        self.timer.start()
        self.record_and_display_memory()

    def set_interval(self, interval_sec):
        """
        Apply a new monitoring interval to the internal timer.

        The value is clamped to at least 1 second.

        Args:
            interval_sec (int):
                Interval in seconds.
        """
        self.interval_sec = max(1, interval_sec)
        self.timer.setInterval(self.interval_sec * 1000)

    def save_interval(self):
        """
        Save the user-entered interval to settings and apply it immediately.

        Behavior:

        - Reads the interval from ``self.interval_input``.
        - Updates ``self.timer`` interval.
        - Persists the value to settings under ``memory_interval_sec``.
        - Writes an info/error message into ``self.text_area``.

        Note:
            - This method only validates that the input can be parsed as an integer.
            - Non-integer input is treated as an error.
        """
        try:
            interval = int(self.interval_input.text())
            self.set_interval(interval)

            settings = ConfigManager.load()
            settings["memory_interval_sec"] = interval
            ConfigManager.save(settings)

            self.text_area.append(f"[INFO] 간격이 {interval}초로 변경되어 저장되었습니다.\n")
        except ValueError:
            self.text_area.append("[ERROR] 숫자를 입력하세요.\n")

    def record_and_display_memory(self):
        """
        Sample current RSS memory usage, append it to the log file, and render it in the UI.

        Output format:
            ``[<timestamp>] Memory: <MB> MB``

        Warning behavior:
            If the sampled memory exceeds a fixed threshold (currently 400 MB),
            the log line is marked with ``[WARNING]`` and colored red in the UI.

        Failures:
            Any unexpected exception is appended to the UI output area as plain text.
        """
        try:
            process = psutil.Process(os.getpid())
            mem = process.memory_info().rss / 1024 ** 2
            timestamp = datetime.now()
            is_warning = mem >= 400
            log = f"[{timestamp}] Memory: {mem:.2f} MB"

            if is_warning:
                log += "  [WARNING] Memory usage high!"

            # Append log to file
            with open(paths.MEMORY_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log + "\n")

            # Insert styled text into text area
            cursor = self.text_area.textCursor()
            cursor.movePosition(QTextCursor.End)

            fmt = QTextCharFormat()
            fmt.setForeground(QColor("red") if is_warning else QColor("black"))
            cursor.insertText(log + "\n", fmt)

            self.text_area.setTextCursor(cursor)
            self.text_area.ensureCursorVisible()

        except Exception as e:
            self.text_area.append(f"Error: {e}")

    def close_monitor(self):
        """
        Stop the monitoring timer and close the widget.
        """
        self.timer.stop()
        self.close()