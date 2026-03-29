# -*- coding: utf-8 -*-
"""
:File: EuljiroBible/gui/utils/keyword_highlight_delegate.py
:Author: Benjamin Jaedon Choi - https://github.com/saintbenjamin
:Affiliated Church: The Eulji-ro Presbyterian Church [대한예수교장로회(통합) 을지로교회]
:Address: The Eulji-ro Presbyterian Church, 24-10, Eulji-ro 20-gil, Jung-gu, Seoul 04549, South Korea
:Telephone: +82-2-2266-3070
:E-mail: euljirochurch [at] G.M.A.I.L. (replace [at] with @ and G.M.A.I.L as you understood.)
:License: MIT License with Attribution Requirement (see LICENSE file for details); Copyright (c) 2025 The Eulji-ro Presbyterian Church.

Provides a `QStyledItemDelegate` that highlights specified keywords in red
within a `QTextDocument`, supporting HTML formatting and line wrapping.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtGui import QTextDocument
from PySide6.QtCore import QPoint

class KeywordHighlightDelegate(QStyledItemDelegate):
    """
    Item delegate that highlights keywords in keyword-search result cells.

    This delegate renders cell text via QTextDocument so that:

    - HTML formatting (keyword spans) is supported
    - multiline text is wrapped and drawn correctly
    - selected-row background rendering remains consistent with Qt styles

    Attributes:
        keywords (List[str]): Keywords to highlight. Each keyword is highlighted by
            wrapping exact string matches in an HTML <span> with a colored style.
    """

    def __init__(self, keywords, parent=None):
        """
        Initialize the delegate.

        Args:
            keywords (List[str]): List of keywords to highlight.
            parent (QWidget | None): Optional parent widget.
        """
        super().__init__(parent)
        self.keywords = keywords  # List[str]

    def paint(self, painter, option, index):
        """
        Paint the table cell using HTML rendering with keyword highlights.

        This method:

        - draws the row background (selected vs non-selected)
        - converts the model text into highlighted HTML
        - uses QTextDocument to render HTML with wrapping inside the cell rectangle

        Args:
            painter (QPainter): Painter used to draw the item.
            option (QStyleOptionViewItem): Style options for the item.
            index (QModelIndex): Model index for the item being painted.
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
        Convert plain text into HTML with keyword highlights.

        This escapes HTML-sensitive characters, converts newlines to <br>,
        and wraps each keyword occurrence with an HTML <span> marker.

        Args:
            text (str): Original cell text.

        Returns:
            str: HTML-formatted string with highlighted keywords.
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