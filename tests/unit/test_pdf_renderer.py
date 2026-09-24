"""Unit tests for ReportLab Platypus PDF renderer."""

from pathlib import Path

from pypdf import PdfReader

from chatprint.models import (
    CodeBlock,
    Conversation,
    HeadingBlock,
    ListBlock,
    Message,
    ParagraphBlock,
    Role,
    TableBlock,
)
from chatprint.pdf.renderer import render_conversation_to_pdf


def test_pdf_renderer_creates_valid_readable_pdf(tmp_path: Path):
    dest_pdf = tmp_path / "test_output.pdf"

    conv = Conversation(
        title="Test Conversation on Distributed Systems",
        source="Google Gemini AI Mode",
        original_filename="gemini.mhtml",
        messages=[
            Message(
                role=Role.USER,
                blocks=[ParagraphBlock(text="What is the CAP theorem?")],
                order=1,
            ),
            Message(
                role=Role.ASSISTANT,
                blocks=[
                    HeadingBlock(level=2, text="CAP Theorem Breakdown"),
                    ParagraphBlock(
                        text="In theoretical computer science, the CAP theorem states that any distributed data store can only provide two of three guarantees: Consistency, Availability, and Partition tolerance."
                    ),
                    ListBlock(
                        items=[
                            "Consistency: Every read receives the most recent write or an error.",
                            "Availability: Every non-failing node returns a response.",
                            "Partition Tolerance: The system continues to operate despite network drops.",
                        ]
                    ),
                    CodeBlock(
                        code="def simulate_partition():\n    return {'status': 'split-brain'}",
                        language="python",
                    ),
                    TableBlock(
                        headers=["System", "Classification"],
                        rows=[["Cassandra", "AP"], ["HBase", "CP"]],
                    ),
                ],
                order=2,
            ),
        ],
    )

    result_path = render_conversation_to_pdf(conv, dest_pdf)

    # 1. File exists and non-empty
    assert result_path.exists()
    assert result_path.stat().st_size > 1000

    # 2. PDF is valid and readable via pypdf
    reader = PdfReader(str(result_path))
    assert len(reader.pages) >= 1

    # 3. Extract text and verify real searchable text
    full_text = " ".join(page.extract_text() for page in reader.pages)
    assert "CAP theorem" in full_text
    assert "Consistency" in full_text
    assert "simulate_partition" in full_text
    assert "Cassandra" in full_text
    assert "Page 1 of" in full_text
    assert "Google Gemini AI Mode" in full_text
