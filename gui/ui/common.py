# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/ui/common.py
Provides reusable UI widgets such as buttons, checkboxes, and loading indicator.
Includes utility wrappers for QPushButton creation with SVG icons and dynamic sizing.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtWidgets import QPushButton, QCheckBox, QWidget, QApplication, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPainter, QPen, QIcon


def create_button(text, callback=None):
    """
    Creates a QPushButton with optional click callback.

    Args:
        text (str): Text to display on the button.
        callback (function, optional): Slot to connect to clicked() signal.

    Returns:
        QPushButton: The configured button.
    """
    btn = QPushButton(text)
    if callback:
        btn.clicked.connect(callback)
    return btn


def create_checkbox(text, checked=False, callback=None):
    """
    Creates a QCheckBox with optional initial state and signal connection.

    Args:
        text (str): Label text next to the checkbox.
        checked (bool): Whether the checkbox is initially checked.
        callback (function, optional): Slot for stateChanged signal.

    Returns:
        QCheckBox: The configured checkbox.
    """
    cb = QCheckBox(text)
    cb.setChecked(checked)
    if callback:
        cb.stateChanged.connect(callback)
    return cb


def create_svg_text_button(svg_path, text, icon_size=20, tooltip="", callback=None):
    """
    Creates a QPushButton with SVG icon and text.

    Args:
        svg_path (str): Path to SVG icon.
        text (str): Button label.
        icon_size (int): Icon size in pixels (default: 20).
        tooltip (str): Tooltip text.
        callback (function, optional): Slot for clicked() signal.

    Returns:
        QPushButton: The configured icon + text button.
    """
    btn = QPushButton(text)
    icon = QIcon(svg_path)
    btn.setIcon(icon)
    btn.setIconSize(QSize(icon_size, icon_size))
    btn.setFont(QApplication.font())
    btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    btn.setMinimumHeight(btn.sizeHint().height())

    if tooltip:
        btn.setToolTip(tooltip)
    if callback:
        btn.clicked.connect(callback)

    return btn


class LoadingIndicator(QWidget):
    """
    A spinning arc-based loading indicator widget.
    Can be shown during background loading operations.
    """

    def __init__(self, parent=None):
        """
        Initializes the spinning loader.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.setFixedSize(50, 50)

    def start(self):
        """
        Starts the loading animation.
        """
        self.angle = 0
        self.show()
        self.timer.start(50)

    def stop(self):
        """
        Stops the animation and hides the widget.
        """
        self.timer.stop()
        self.hide()

    def update_angle(self):
        """
        Advances the angle for the rotating arc.
        """
        self.angle += 10
        if self.angle >= 360:
            self.stop()
        self.update()

    def paintEvent(self, event):
        """
        Paints the spinning arc using QPainter.

        Args:
            event (QPaintEvent): Internal paint event.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(5, 5, -5, -5)
        pen = QPen(Qt.gray, 5)
        painter.setPen(pen)
        painter.drawArc(rect, 90 * 16, -self.angle * 16)

    def showEvent(self, event):
        """
        Centers the widget within its parent on show.

        Args:
            event (QShowEvent): Widget shown.
        """
        super().showEvent(event)
        if self.parent():
            self.setGeometry(
                (self.parent().width() - self.width()) // 2,
                (self.parent().height() - self.height()) // 2,
                self.width(),
                self.height()
            )

    def resizeEvent(self, event):
        """
        Keeps widget centered when parent resizes.

        Args:
            event (QResizeEvent): Resize trigger.
        """
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(
                (self.parent().width() - self.width()) // 2,
                (self.parent().height() - self.height()) // 2,
                self.width(),
                self.height()
            )

    def center_in_parent(self):
        """
        Repositions the indicator to be centered manually.
        """
        if self.parent():
            pw, ph = self.parent().width(), self.parent().height()
            sw, sh = self.width(), self.height()
            self.move((pw - sw) // 2, (ph - sh) // 2)