"""Unit tests for GeminiProvider."""

from pathlib import Path

from chatprint.input.html_reader import read_html_file
from chatprint.input.mhtml_reader import read_mhtml_file
from chatprint.models import Role
from chatprint.providers.gemini import GeminiProvider


def test_gemini_detection_confidence(gemini_simple_html: Path, gemini_with_sidebar_mhtml: Path):
    provider = GeminiProvider()
    doc_html = read_html_file(gemini_simple_html)
    score_html = provider.detect_confidence(doc_html.soup, doc_html.raw_html, doc_html.metadata)
    assert score_html >= 0.7

    doc_mhtml = read_mhtml_file(gemini_with_sidebar_mhtml)
    score_mhtml = provider.detect_confidence(doc_mhtml.soup, doc_mhtml.raw_html, doc_mhtml.metadata)
    assert score_mhtml >= 0.7


def test_gemini_extraction_simple(gemini_simple_html: Path):
    provider = GeminiProvider()
    doc = read_html_file(gemini_simple_html)
    conversation = provider.extract(doc.soup, doc.resources, gemini_simple_html.name)

    assert conversation.source == "Google Gemini AI Mode"
    assert "is kilowatt a good company" in conversation.title.lower()
    assert len(conversation.messages) >= 2

    # Check User message
    user_msg = conversation.messages[0]
    assert user_msg.role == Role.USER
    assert "is kilowatt a good company" in user_msg.plain_text.lower()

    # Check Assistant message
    assistant_msg = conversation.messages[1]
    assert assistant_msg.role == Role.ASSISTANT
    plain_text = assistant_msg.plain_text
    assert "Kilowatt" in plain_text
    assert "Work Culture" in plain_text
    assert "Positives" in plain_text

    # Verify Unwanted UI is completely stripped
    all_text = " ".join(m.plain_text for m in conversation.messages)
    assert "user@example.com" not in all_text
    assert "Sign In" not in all_text
    assert "People also ask" not in all_text
    assert "Sponsored Ads" not in all_text
    assert "Copy response" not in all_text


def test_gemini_multiturn(gemini_multiturn_html: Path):
    provider = GeminiProvider()
    doc = read_html_file(gemini_multiturn_html)
    conversation = provider.extract(doc.soup, doc.resources, gemini_multiturn_html.name)

    assert len(conversation.messages) == 4
    assert conversation.messages[0].role == Role.USER
    assert "asyncio" in conversation.messages[0].plain_text
    assert conversation.messages[1].role == Role.ASSISTANT
    assert conversation.messages[2].role == Role.USER
    assert "code snippet" in conversation.messages[2].plain_text
    assert conversation.messages[3].role == Role.ASSISTANT
    assert "asyncio.run" in conversation.messages[3].plain_text


def test_gemini_ai_mode_multiturn():
    from bs4 import BeautifulSoup
    html = """
    <html>
      <head><title>is kilowatt a good company - Google Search</title></head>
      <body>
        <div id="header"><button>Sign In</button></div>
        <div id="searchform"><input name="q" value="is kilowatt a good company" /></div>
        <div id="rhs"><div>Right sidebar recommendations</div></div>
        <main>
          <h2>You said: is kilowatt a good company 10:24 AM</h2>
          <div>
            <h3>AI Mode reply for is kilowatt a good company</h3>
            <div>
              <div class="mZJni">
                <button aria-label="Share">Share</button>
                <button aria-label="Copy">Copy</button>
                <p>Kilowott is a tech company specializing in design and digital engineering.</p>
                <ul>
                  <li>Strong learning culture</li>
                  <li>Good work life balance</li>
                </ul>
              </div>
            </div>
          </div>
          <h2>You sent: what about salary? and said: tell me the range</h2>
          <div>
            <h3>AI Mode reply for what about salary?</h3>
            <div>
              <div class="mZJni">
                <p>Salary ranges vary by role and seniority level.</p>
              </div>
            </div>
          </div>
        </main>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    provider = GeminiProvider()
    assert provider.detect_confidence(soup, html, {}) >= 0.8

    conv = provider.extract(soup, {}, "test.html")
    assert len(conv.messages) == 4
    assert conv.messages[0].role == Role.USER
    assert conv.messages[0].plain_text == "is kilowatt a good company"
    assert conv.messages[1].role == Role.ASSISTANT
    assert "Kilowott is a tech company" in conv.messages[1].plain_text
    assert conv.messages[2].role == Role.USER
    assert conv.messages[2].plain_text == "tell me the range"
    assert conv.messages[3].role == Role.ASSISTANT
    assert "Salary ranges vary" in conv.messages[3].plain_text

    # Verify UI elements stripped
    all_text = " ".join(m.plain_text for m in conv.messages)
    assert "Sign In" not in all_text
    assert "Right sidebar recommendations" not in all_text
    assert "Share" not in all_text
    assert "Copy" not in all_text
