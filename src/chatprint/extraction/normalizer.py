"""Content normalization: converts DOM elements to structured ContentBlocks."""

import html
import re

from bs4 import NavigableString, Tag

from chatprint.models import (
    CodeBlock,
    ContentBlock,
    HeadingBlock,
    ListBlock,
    ParagraphBlock,
    TableBlock,
)


def normalize_text(text: str) -> str:
    """Normalize whitespace and decode HTML entities."""
    if not text:
        return ""
    text = html.unescape(text)
    # Replace non-breaking spaces
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    # Normalize consecutive spaces within lines
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _extract_text_with_inline_formatting(tag: Tag) -> str:
    """Convert child tags to readable text preserving basic emphasis and links."""
    parts: list[str] = []
    for child in tag.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
        elif isinstance(child, Tag):
            name = child.name.lower()
            inner = _extract_text_with_inline_formatting(child)
            if name in ("strong", "b"):
                parts.append(f"**{inner}**")
            elif name in ("em", "i"):
                parts.append(f"*{inner}*")
            elif name == "code":
                parts.append(f"`{inner}`")
            elif name == "br":
                parts.append("\n")
            elif name == "a":
                href = child.get("href")
                if href and not href.startswith("#") and not href.startswith("javascript:"):
                    parts.append(f"[{inner}]({href})")
                else:
                    parts.append(inner)
            else:
                parts.append(inner)
    text = "".join(parts)
    return normalize_text(text)


def element_to_content_blocks(container: Tag) -> list[ContentBlock]:
    """Parse an HTML container element into a list of structured ContentBlock instances.

    Args:
        container: BeautifulSoup Tag containing message content.

    Returns:
        List of structured ContentBlock objects.
    """
    blocks: list[ContentBlock] = []

    for child in container.children:
        if isinstance(child, NavigableString):
            raw = str(child).strip()
            if raw:
                blocks.append(ParagraphBlock(text=normalize_text(raw)))
            continue

        if not isinstance(child, Tag):
            continue

        name = child.name.lower()

        # Headings
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(name[1])
            text = normalize_text(child.get_text())
            if text:
                blocks.append(HeadingBlock(level=level, text=text))
            continue

        # Code blocks: <pre> or element containing <code>
        if name == "pre" or (name == "div" and child.find("pre")):
            pre_tag = child if name == "pre" else child.find("pre")
            code_tag = pre_tag.find("code") if pre_tag else None
            code_text = (code_tag or pre_tag).get_text()
            # Try to extract language from class="language-python" etc.
            lang = ""
            classes = (code_tag.get("class") if code_tag else None) or (pre_tag.get("class") if pre_tag else None) or []
            for cls in classes:
                if cls.startswith("language-"):
                    lang = cls.replace("language-", "")
                    break
            clean_code = code_text.rstrip()
            if clean_code:
                blocks.append(CodeBlock(code=clean_code, language=lang))
            continue

        # Lists: <ul>, <ol>
        if name in ("ul", "ol"):
            items: list[str] = []
            for li in child.find_all("li", recursive=False):
                item_text = _extract_text_with_inline_formatting(li)
                if item_text:
                    items.append(item_text)
            if items:
                blocks.append(ListBlock(items=items, ordered=(name == "ol")))
            continue

        # Tables: <table>
        if name == "table":
            headers: list[str] = []
            rows: list[list[str]] = []
            thead = child.find("thead")
            if thead:
                for th in thead.find_all(["th", "td"]):
                    headers.append(normalize_text(th.get_text()))
            for tr in child.find_all("tr"):
                # If row is inside thead and headers were extracted, skip
                if thead and tr.find_parent("thead"):
                    continue
                row_cells = [normalize_text(td.get_text()) for td in tr.find_all(["td", "th"])]
                if row_cells:
                    # If no headers yet and all are th, use as header
                    if not headers and all(cell.name == "th" for cell in tr.find_all(["td", "th"])):
                        headers = row_cells
                    else:
                        rows.append(row_cells)
            if headers or rows:
                blocks.append(TableBlock(headers=headers, rows=rows))
            continue

        # Blockquote
        if name == "blockquote":
            quote_text = normalize_text(child.get_text())
            if quote_text:
                blocks.append(ParagraphBlock(text=f"> {quote_text}"))
            continue

        # Paragraphs or general div/sections
        if name == "p":
            text = _extract_text_with_inline_formatting(child)
            if text:
                blocks.append(ParagraphBlock(text=text))
            continue

        # Nested container div/section: recursively parse if it contains sub-blocks
        if any(child.find(tag_name) for tag_name in ("p", "pre", "ul", "ol", "table", "h1", "h2", "h3", "h4", "h5", "h6")):
            sub_blocks = element_to_content_blocks(child)
            blocks.extend(sub_blocks)
        else:
            text = _extract_text_with_inline_formatting(child)
            if text:
                blocks.append(ParagraphBlock(text=text))

    return blocks
