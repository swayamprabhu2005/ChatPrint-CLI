"""Layout and text formatting helpers for ReportLab flowables."""

import html
import re

from reportlab.graphics.shapes import Drawing, Line

from ai_conversation.pdf.styles import BORDER_LIGHT


def safe_reportlab_text(text: str) -> str:
    """Escape text for ReportLab XML/HTML Paragraph parsing and convert markdown tags.

    Converts:
        **bold** -> <b>bold</b>
        *italic* -> <i>italic</i>
        `code` -> <font face="Courier">code</font>
    """
    if not text:
        return ""

    # Convert characters that break XML
    text = html.escape(text)

    # Convert markdown bold **...**
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    # Convert markdown italic *...*
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)

    # Convert markdown code `...`
    text = re.sub(r"`(.+?)`", r'<font face="Courier" color="#334155">\1</font>', text)

    # Convert links [text](url)
    text = re.sub(r"\[(.+?)\]\((https?://[^\s)]+)\)", r'<link href="\2" color="#2563eb"><u>\1</u></link>', text)

    return text


def create_divider_line(width: float = 520, thickness: float = 0.5) -> Drawing:
    """Create a subtle horizontal dividing line."""
    d = Drawing(width, 10)
    d.add(Line(0, 5, width, 5, strokeColor=BORDER_LIGHT, strokeWidth=thickness))
    return d
