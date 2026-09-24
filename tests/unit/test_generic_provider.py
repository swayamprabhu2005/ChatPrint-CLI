"""Unit tests for GenericProvider."""

from bs4 import BeautifulSoup

from chatprint.providers.generic import GenericProvider


def test_generic_provider_extraction():
    provider = GenericProvider()
    html = """
    <html>
    <head><title>Custom Assistant Chat</title></head>
    <body>
        <main>
            <div class="chat-container">
                <div class="turn-user"><p>Explain photosynthesis.</p></div>
                <div class="turn-bot"><p>Photosynthesis is the process used by plants to convert light energy into chemical energy.</p></div>
            </div>
        </main>
    </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    conversation = provider.extract(soup, {}, "custom.html")

    assert conversation.source == "Generic AI Webpage"
    assert "Custom Assistant Chat" in conversation.title
    assert len(conversation.messages) >= 1
    all_text = " ".join(m.plain_text for m in conversation.messages)
    assert "photosynthesis" in all_text.lower()
