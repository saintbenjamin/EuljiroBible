# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/monitor_memory.py
Popup window to monitor current memory usage periodically.
Logs to file and provides GUI interface for checking memory in real time.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
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
    Popup QWidget that monitors and displays Python process memory usage.
    Automatically logs to memory_log.txt and shows warnings when exceeding threshold.
    """

    def __init__(self, interval_sec=5, parent=None):
        """
        Initializes the memory monitor widget and UI layout.

        Args:
            interval_sec (int): Monitoring interval in seconds.
            parent (QWidget, optional): Parent window.
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
        Sets the interval between memory checks.

        Args:
            interval_sec (int): Interval in seconds.
        """
        self.interval_sec = max(1, interval_sec)
        self.timer.setInterval(self.interval_sec * 1000)

    def save_interval(self):
        """
        Saves the user-entered interval to the settings file and updates the timer.
        Displays confirmation or error in the log area.
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
        Measures current memory usage, logs to file, and displays in UI.
        Highlights warnings when memory exceeds 400MB.
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
        Stops the timer and closes the widget.
        """
        self.timer.stop()
        self.close()