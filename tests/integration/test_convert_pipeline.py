"""Integration tests for the complete conversion pipeline."""

from pathlib import Path

from pypdf import PdfReader

from chatprint.input.detector import InputFormat, detect_format
from chatprint.input.mhtml_reader import read_mhtml_file
from chatprint.pdf.renderer import render_conversation_to_pdf
from chatprint.providers import detect_best_provider
from chatprint.utils.files import resolve_output_pdf_path


def test_gemini_full_conversion_pipeline(gemini_with_sidebar_mhtml: Path, tmp_path: Path):
    # Record original mtime & size to ensure original is NEVER modified
    orig_stat = gemini_with_sidebar_mhtml.stat()

    # 1. Format Detection
    fmt = detect_format(gemini_with_sidebar_mhtml)
    assert fmt == InputFormat.MHTML

    # 2. Reading
    doc = read_mhtml_file(gemini_with_sidebar_mhtml)

    # 3. Provider detection & extraction
    provider, confidence = detect_best_provider(doc.soup, doc.raw_html, doc.metadata)
    assert provider.name == "gemini"
    assert confidence >= 0.7

    conversation = provider.extract(doc.soup, doc.resources, gemini_with_sidebar_mhtml.name)
    assert conversation.user_messages_count >= 1
    assert conversation.assistant_messages_count >= 1

    # 4. PDF Generation
    out_dir = tmp_path / "output_pdf"
    target_pdf = resolve_output_pdf_path(gemini_with_sidebar_mhtml, output_dir=out_dir)
    final_path = render_conversation_to_pdf(conversation, target_pdf)

    assert final_path.exists()
    assert final_path.suffix == ".pdf"

    # 5. Verify PDF content with pypdf
    reader = PdfReader(str(final_path))
    assert len(reader.pages) >= 1
    full_text = " ".join(p.extract_text() for p in reader.pages)

    # Verify conversation is present
    assert "is kilowatt a good company" in full_text
    assert "Positives" in full_text
    assert "Work Culture" in full_text

    # Verify unwanted UI is NOT present in PDF
    assert "user@gmail.com" not in full_text
    assert "Right Sidebar Ad Widget" not in full_text
    assert "Google Footer Links" not in full_text

    # 6. Verify original file is untouched
    new_stat = gemini_with_sidebar_mhtml.stat()
    assert new_stat.st_mtime == orig_stat.st_mtime
    assert new_stat.st_size == orig_stat.st_size


def test_chatgpt_full_conversion_pipeline(chatgpt_multiturn_mhtml: Path, tmp_path: Path):
    doc = read_mhtml_file(chatgpt_multiturn_mhtml)
    provider, _ = detect_best_provider(doc.soup, doc.raw_html, doc.metadata)
    assert provider.name == "chatgpt"

    conversation = provider.extract(doc.soup, doc.resources, chatgpt_multiturn_mhtml.name)
    assert conversation.total_messages_count == 4

    out_file = tmp_path / "chatgpt_output.pdf"
    render_conversation_to_pdf(conversation, out_file)

    reader = PdfReader(str(out_file))
    full_text = " ".join(p.extract_text() for p in reader.pages)

    assert "Rust" in full_text
    assert "ownership system" in full_text
    assert "borrowed" in full_text
    assert "Chat History Sidebar" not in full_text


def test_safe_file_collision_handling(tmp_path: Path):
    input_file = tmp_path / "my_chat.mhtml"
    input_file.write_text("dummy", encoding="utf-8")

    out_dir = tmp_path / "pdfs"
    out_dir.mkdir()

    # First resolve
    p1 = resolve_output_pdf_path(input_file, output_dir=out_dir)
    assert p1.name == "my_chat.pdf"
    p1.write_text("first", encoding="utf-8")

    # Second resolve without force -> must not overwrite, returns my_chat-1.pdf
    p2 = resolve_output_pdf_path(input_file, output_dir=out_dir, force=False)
    assert p2.name == "my_chat-1.pdf"
    p2.write_text("second", encoding="utf-8")

    # Third resolve without force -> returns my_chat-2.pdf
    p3 = resolve_output_pdf_path(input_file, output_dir=out_dir, force=False)
    assert p3.name == "my_chat-2.pdf"

    # With force=True -> targets my_chat.pdf directly
    p_force = resolve_output_pdf_path(input_file, output_dir=out_dir, force=True)
    assert p_force.name == "my_chat.pdf"
