# -*- coding: utf-8 -*-
"""
File: EuljiroBible/gui/utils/keyword_highlight_delegate.py
Provides a QStyledItemDelegate that highlights specified keywords in red
within a QTextDocument, supporting HTML formatting and line wrapping.

Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
Telephone: +82-2-2266-3070
E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
Copyright (c) 2025 The Eulji-ro Presbyterian Church.
License: MIT License with Attribution Requirement (see LICENSE file for details)
"""

from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtGui import QTextDocument
from PySide6.QtCore import QPoint

class KeywordHighlightDelegate(QStyledItemDelegate):
    """
    Custom delegate to render keyword search results with highlighted terms
    using QTextDocument for HTML and multiline support.

    :param keywords: List of keywords to highlight
    :type keywords: list[str]
    :param parent: Optional parent QWidget
    :type parent: QWidget | None
    """

    def __init__(self, keywords, parent=None):
        super().__init__(parent)
        self.keywords = keywords  # list[str]

    def paint(self, painter, option, index):
        """
        Renders the cell with HTML-formatted text, highlighting keywords.

        :param painter: QPainter object used for rendering
        :type painter: QPainter
        :param option: Styling options for the item
        :type option: QStyleOptionViewItem
        :param index: Index of the model item
        :type index: QModelIndex
        """
        text = index.data()
        if not text:
            return super().paint(painter, option, index)

        painter.save()

        # Draw background depending on selection state
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            painter.fillRect(option.rect, option.backgroundBrush)

        # Convert keywords to HTML-marked-up string
        html = self._highlight_keywords(text)

        # Use QTextDocument for proper HTML rendering and line wrapping
        doc = QTextDocument()
        doc.setDefaultFont(option.font)
        doc.setHtml(html)
        doc.setTextWidth(option.rect.width() - 8)  # Account for horizontal padding

        # Offset drawing to avoid touching borders
        painter.translate(option.rect.topLeft() + QPoint(4, 4))
        doc.drawContents(painter)

        painter.restore()

    def _highlight_keywords(self, text):
        """
        Escapes HTML in the text and wraps matching keywords with red-colored spans.
        Also converts newline characters to <br> for HTML rendering.

        :param text: The original verse text
        :type text: str
        :return: HTML-formatted string with <span> wrapped keywords
        :rtype: str
        """
        # Escape HTML-sensitive characters
        escaped_text = (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br>")  # Convert newlines to HTML line breaks
        )

        # Wrap keywords in <span style='color:red'>
        for kw in self.keywords:
            if not kw:
                continue
            escaped_kw = kw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            escaped_text = escaped_text.replace(
                escaped_kw, f"<span style='color:red'>{escaped_kw}</span>"
            )

        return escaped_text