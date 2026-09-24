"""Layout and text formatting helpers for ReportLab flowables."""

import contextlib
import html
import re

from reportlab.graphics.shapes import Drawing, Line

from chatprint.pdf.styles import BORDER_LIGHT


def safe_reportlab_text(text: str) -> str:
    """Escape text for ReportLab XML/HTML Paragraph parsing and convert markdown tags.

    Converts:
        **bold** -> <b>bold</b>
        *italic* -> <i>italic</i>
        `code` -> <font face="Courier">code</font>
    """
    if not text:
        return ""

    # Replace currency symbols not in standard PDF Type 1 fonts
    text = text.replace("₹", "Rs. ")

    # Convert characters that break XML
    text = html.escape(text)

    # Convert markdown bold **...**
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.DOTALL)

    # Convert markdown italic *...*
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text, flags=re.DOTALL)

    # Convert markdown code `...`
    text = re.sub(r"`(.+?)`", r'<font face="Courier" color="#334155">\1</font>', text, flags=re.DOTALL)

    # Convert links [text](url)
    text = re.sub(r"\[(.+?)\]\((https?://[^\s)]+)\)", r'<link href="\2" color="#1a73e8"><u>\1</u></link>', text)

    # Balance any interleaved or unclosed tags
    with contextlib.suppress(Exception):
        from bs4 import BeautifulSoup
        text = str(BeautifulSoup(text, "html.parser"))

    return text


def create_divider_line(width: float = 520, thickness: float = 0.5) -> Drawing:
    """Create a subtle horizontal dividing line."""
    d = Drawing(width, 10)
    d.add(Line(0, 5, width, 5, strokeColor=BORDER_LIGHT, strokeWidth=thickness))
    return d
