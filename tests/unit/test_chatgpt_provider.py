"""Unit tests for ChatGPTProvider."""

from pathlib import Path

from chatprint.input.html_reader import read_html_file
from chatprint.input.mhtml_reader import read_mhtml_file
from chatprint.models import CodeBlock, Role, TableBlock
from chatprint.providers.chatgpt import ChatGPTProvider


def test_chatgpt_detection_confidence(chatgpt_simple_html: Path, chatgpt_multiturn_mhtml: Path):
    provider = ChatGPTProvider()
    doc_html = read_html_file(chatgpt_simple_html)
    score_html = provider.detect_confidence(doc_html.soup, doc_html.raw_html, doc_html.metadata)
    assert score_html >= 0.7

    doc_mhtml = read_mhtml_file(chatgpt_multiturn_mhtml)
    score_mhtml = provider.detect_confidence(doc_mhtml.soup, doc_mhtml.raw_html, doc_mhtml.metadata)
    assert score_mhtml >= 0.7


def test_chatgpt_simple_extraction(chatgpt_simple_html: Path):
    provider = ChatGPTProvider()
    doc = read_html_file(chatgpt_simple_html)
    conversation = provider.extract(doc.soup, doc.resources, chatgpt_simple_html.name)

    assert conversation.source == "ChatGPT"
    assert "Quantum Computing" in conversation.title
    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == Role.USER
    assert "qubit" in conversation.messages[0].plain_text
    assert conversation.messages[1].role == Role.ASSISTANT
    assert "superposition" in conversation.messages[1].plain_text

    # Unwanted UI stripped
    all_text = " ".join(m.plain_text for m in conversation.messages)
    assert "History: Conversation 1" not in all_text
    assert "Upgrade to Plus" not in all_text
    assert "ChatGPT can make mistakes" not in all_text


def test_chatgpt_multiturn_mhtml(chatgpt_multiturn_mhtml: Path):
    provider = ChatGPTProvider()
    doc = read_mhtml_file(chatgpt_multiturn_mhtml)
    conversation = provider.extract(doc.soup, doc.resources, chatgpt_multiturn_mhtml.name)

    assert len(conversation.messages) == 4
    assert conversation.user_messages_count == 2
    assert conversation.assistant_messages_count == 2
    assert "Rust" in conversation.title
    assert "ownership system" in conversation.messages[1].plain_text


def test_chatgpt_code_and_table(chatgpt_with_code_html: Path):
    provider = ChatGPTProvider()
    doc = read_html_file(chatgpt_with_code_html)
    conversation = provider.extract(doc.soup, doc.resources, chatgpt_with_code_html.name)

    assistant_msg = conversation.messages[1]
    has_code = any(isinstance(b, CodeBlock) for b in assistant_msg.blocks)
    has_table = any(isinstance(b, TableBlock) for b in assistant_msg.blocks)

    assert has_code
    assert has_table

    # Find the table block and verify content
    table_block = next(b for b in assistant_msg.blocks if isinstance(b, TableBlock))
    assert "Flask" in table_block.headers
    assert "FastAPI" in table_block.headers
