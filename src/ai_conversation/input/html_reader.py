"""Reader for standalone HTML files."""

import re
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup

from ai_conversation.errors import InvalidInputError


@dataclass
class HTMLDocument:
    """Represents a loaded HTML document."""

    raw_html: str
    file_path: Path
    title: str = ""
    resources: dict[str, bytes] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def soup(self) -> BeautifulSoup:
        """Parse and return a BeautifulSoup DOM tree."""
        return BeautifulSoup(self.raw_html, "html.parser")


_CHARSET_RE = re.compile(r'charset=["\']?([a-zA-Z0-9_-]+)', re.IGNORECASE)


def read_html_file(file_path: Path) -> HTMLDocument:
    """Read and decode an HTML file with robust encoding detection.

    Args:
        file_path: Path to HTML file.

    Returns:
        HTMLDocument instance.

    Raises:
        InvalidInputError: If reading fails.
    """
    path = Path(file_path)
    try:
        raw_bytes = path.read_bytes()
    except OSError as e:
        raise InvalidInputError(
            f"Failed to read file: {path} ({e})",
            suggestion="Check file permissions.",
        ) from e

    # Detect encoding: look for meta charset
    encoding = "utf-8"
    match = _CHARSET_RE.search(raw_bytes[:2048].decode("ascii", errors="ignore"))
    if match:
        encoding = match.group(1).lower()

    decoded_html: str
    try:
        decoded_html = raw_bytes.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        try:
            decoded_html = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            decoded_html = raw_bytes.decode("latin1", errors="replace")

    # Extract title quickly if present
    title = ""
    soup = BeautifulSoup(decoded_html, "html.parser")
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    metadata: dict[str, str] = {}
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property")
        content = meta.get("content")
        if name and content:
            metadata[name] = content

    return HTMLDocument(
        raw_html=decoded_html,
        file_path=path,
        title=title,
        metadata=metadata,
    )
