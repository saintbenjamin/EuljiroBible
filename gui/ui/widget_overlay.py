# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/widget_overlay.py
Description: Defines an overlay widget for displaying Bible verses in EuljiroBible.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

import os
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QRect, QFileSystemWatcher, QTimer
from PySide6.QtGui import QFont, QKeyEvent

from gui.config.config_manager import ConfigManager
from gui.utils.logger import log_error_with_dialog

class WidgetOverlay(QWidget):
    """
    Widget that displays Bible verses as an overlay widget, with file watching and polling support.
    """

    def __init__(self, font_family, font_size, text_color, bg_color, alpha, mode, geometry, parent=None):
        """
        Initializes the overlay widget.

        Args:
            font_family (str): Font family for text.
            font_size (int): Base font size.
            text_color (str): Text color in hex.
            bg_color (str): Background color in hex.
            alpha (float): Background transparency.
            mode (str): 'fullscreen' or 'windowed'.
            geometry (QRect): Initial window geometry.
            parent (QWidget, optional): Parent widget.
        """        
        super().__init__()
        self.mode = mode
        self.base_font_size = font_size

        settings = ConfigManager.load()

        self.last_text = ""
        
        poll_enabled = settings.get("poll_enabled", True)
        if poll_enabled:
            interval = settings.get("poll_interval", 1000)
            self.poll_timer = QTimer(self)
            self.poll_timer.timeout.connect(self.poll_file)
            self.poll_timer.start(interval)

        self.setGeometry(geometry)
        if mode == "fullscreen":
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.showFullScreen()
        else:
            self.setWindowFlags(Qt.WindowType.Window)
            self.resize(800, 600)

        lang = ConfigManager.load().get("last_language", "ko")
        self.setWindowTitle("대한예수교장로회(통합) 을지로교회" if lang == "ko" else "The Eulji-ro Presbyterian Church (Tonghap)")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)

        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setFont(QFont(font_family, font_size, QFont.Weight.Bold))

        r, g, b = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
        alpha_val = alpha
        self.bg_style = f"background-color: rgba({r}, {g}, {b}, {alpha_val}); background-clip: padding-box;"
        self.text_color = text_color
        self.apply_stylesheet()

        layout.addWidget(self.label)

        self.verse_path = ConfigManager.load().get("output_path", "verse_output.txt")
        self.watcher = QFileSystemWatcher([self.verse_path])
        self.watcher.fileChanged.connect(self.on_file_changed)
        self.reload_text()

    def apply_settings(self):
        """
        Applies updated display settings from configuration.
        """
        settings = ConfigManager.load()
        font_family = settings.get("display_font_family", "Arial")
        font_size = int(settings.get("display_font_size", 36))
        font_weight = settings.get("display_font_weight", QFont.Weight.Normal.value)
        text_color = settings.get("display_text_color", "#000000")
        bg_color = settings.get("display_bg_color", "#FFFFFF")
        alpha = settings.get("display_bg_alpha", 1.0)

        self.base_font_size = font_size

        font = QFont(font_family, font_size)

        if font_weight > 99:
            font.setWeight(QFont.Weight(font_weight))
        else:
            font.setWeight(font_weight)

        self.label.setFont(font)

        r, g, b = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
        self.bg_style = f"background-color: rgba({r}, {g}, {b}, {alpha});"
        self.text_color = text_color
        self.apply_stylesheet()
        self.adjust_font_size(self.label.text())

    def apply_stylesheet(self):
        """
        Applies the current text color and background style.
        """
        if self.mode == "fullscreen":
            border_radius = "border-radius: 30px; padding: 40px;"
        else:
            border_radius = "margin: 0px; padding: 0px; border: none;" 

        self.label.setStyleSheet(f"""
            color: {self.text_color};
            {self.bg_style}
            {border_radius}
        """)

    def adjust_font_size(self, text):
        """
        Adjusts font size dynamically to fit text within the widget.

        Args:
            text (str): Text to fit.
        """
        available_width = int(self.width() * 0.8)
        available_height = int(self.height() * 0.8)
        font = self.label.font()
        font_size = self.base_font_size

        while font_size > 10:
            font.setPointSize(font_size)
            self.label.setFont(font)
            metrics = self.label.fontMetrics()
            rect = metrics.boundingRect(QRect(0, 0, available_width, available_height), Qt.TextFlag.TextWordWrap, text)

            # If text fits in the available space, stop reducing size
            if rect.width() <= available_width and rect.height() <= available_height:
                break

            font_size -= 2  # Decrease size and try again

        self.label.setFont(font)

    def display_text(self, text):
        """
        Displays the given text with adjusted font size.

        Args:
            text (str): Text to display.
        """
        self.label.setText(text)
        self.adjust_font_size(text)

    def read_verse_file(self):
        """
        Reads the verse output file.

        Returns:
            str or None: File content if successful, else None.
        """
        try:
            with open(self.verse_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            log_error_with_dialog(e)
            log_error_with_dialog(f"[WidgetOverlay.read_verse_file] Failed to read verse file: {self.verse_path}")
            return None

    def reload_text(self):
        """
        Reloads and updates the displayed text from the verse file.
        """
        if os.path.exists(self.verse_path):
            verse_text = self.read_verse_file()
            if verse_text is None:
                return

            self.last_text = verse_text

            if verse_text == "":
                # If verse file is intentionally emptied, close the overlay
                self.close()
            else:
                self.display_text(verse_text)

    def poll_file(self):
        """
        Periodically checks the verse file for changes and updates display.
        Used when polling is enabled.
        """
        if os.path.exists(self.verse_path):
            verse_text = self.read_verse_file()
            if verse_text is None:
                return
            if verse_text != self.last_text:
                self.reload_text()

    def on_file_changed(self, path):
        """
        Handles file system notification of verse file changes.
        Used when QFileSystemWatcher triggers a change event.

        Args:
            path (str): Path of the changed file.
        """
        if os.path.exists(path):
            self.watcher.addPath(path)
            self.reload_text()

    def resizeEvent(self, event):
        """
        Handles widget resize events and adjusts font size.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        if hasattr(self, "label") and self.label.text():
            self.adjust_font_size(self.label.text())

    def keyPressEvent(self, event: QKeyEvent):
        """
        Closes the overlay if ESC is pressed.
        """
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """
        Handles widget close events and stops polling/watching.

        Args:
            event (QCloseEvent): The close event.
        """
        if hasattr(self, 'poll_timer'):
            self.poll_timer.stop()
        if hasattr(self, 'watcher'):
            files = self.watcher.files()
            if files:
                self.watcher.removePaths(files)
        event.accept()