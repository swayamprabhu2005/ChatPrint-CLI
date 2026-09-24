"""Format detection for input conversation files."""

from enum import Enum
from pathlib import Path

from ai_conversation.errors import InvalidInputError, UnsupportedFormatError


class InputFormat(str, Enum):
    """Supported input file formats."""

    MHTML = "mhtml"
    HTML = "html"


_MIME_MARKERS = [
    b"MIME-Version:",
    b"Content-Type: multipart/related",
    b"Snapshot-Content-Location:",
    b"From: <Saved by Blink>",
]


def detect_format(file_path: Path) -> InputFormat:
    """Detect whether a file is MHTML or HTML based on extension and content inspection.

    Args:
        file_path: Path to the target file.

    Returns:
        InputFormat enum member.

    Raises:
        InvalidInputError: If the file does not exist or is not a regular file.
        UnsupportedFormatError: If the format is not recognized.
    """
    path = Path(file_path)
    if not path.exists():
        raise InvalidInputError(
            f"Input file not found: {path}",
            suggestion="Check the file path and confirm the file exists.",
        )
    if not path.is_file():
        raise InvalidInputError(
            f"Input path is not a regular file: {path}",
            suggestion="Provide a valid .mhtml, .mht, .html, or .htm file.",
        )

    suffix = path.suffix.lower()

    # Read first 4KB to check for MIME headers
    try:
        with open(path, "rb") as f:
            header_sample = f.read(4096)
    except OSError as e:
        raise InvalidInputError(
            f"Unable to read file: {path} ({e})",
            suggestion="Check file permissions and ensure it is not locked by another process.",
        ) from e

    # Check for MHTML MIME signatures
    is_mime_content = any(marker.lower() in header_sample.lower() for marker in _MIME_MARKERS)

    if suffix in (".mhtml", ".mht"):
        return InputFormat.MHTML

    if is_mime_content:
        return InputFormat.MHTML

    if suffix in (".html", ".htm"):
        return InputFormat.HTML

    # Fallback inspection: check for html tag in sample
    sample_lower = header_sample.lower()
    if b"<!doctype html" in sample_lower or b"<html" in sample_lower:
        return InputFormat.HTML

    raise UnsupportedFormatError(
        f"Unsupported file format for: {path.name}",
        suggestion="AI Conversation CLI supports .mhtml, .mht, .html, and .htm files.",
    )
