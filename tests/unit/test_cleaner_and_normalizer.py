"""Unit tests for DOM cleaning and element normalization."""

from bs4 import BeautifulSoup

from chatprint.extraction.cleaner import clean_dom
from chatprint.extraction.normalizer import (
    element_to_content_blocks,
    normalize_text,
)
from chatprint.models import (
    CodeBlock,
    HeadingBlock,
    ListBlock,
    ParagraphBlock,
)


def test_clean_dom_removes_scripts_and_hidden():
    html = """
    <div>
        <script>alert('malicious')</script>
        <p>Visible content</p>
        <div style="display: none">Hidden secret</div>
        <button>Click me</button>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    cleaned = clean_dom(soup)
    text = cleaned.get_text()

    assert "Visible content" in text
    assert "malicious" not in text
    assert "Hidden secret" not in text
    assert "Click me" not in text


def test_normalize_text():
    raw = "   Line 1  with   spaces  \n\n\n  Line 2   "
    clean = normalize_text(raw)
    assert clean == "Line 1 with spaces\nLine 2"


def test_element_to_content_blocks_structured():
    html = """
    <div>
        <h2>Section Title</h2>
        <p>This is a paragraph with <b>bold</b> text.</p>
        <ul>
            <li>First item</li>
            <li>Second item</li>
        </ul>
        <pre><code class="language-python">print('hello')</code></pre>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    blocks = element_to_content_blocks(soup.div)

    assert any(isinstance(b, HeadingBlock) and b.text == "Section Title" for b in blocks)
    assert any(isinstance(b, ParagraphBlock) and "bold" in b.text for b in blocks)
    assert any(isinstance(b, ListBlock) and len(b.items) == 2 for b in blocks)
    assert any(isinstance(b, CodeBlock) and "print('hello')" in b.code for b in blocks)
