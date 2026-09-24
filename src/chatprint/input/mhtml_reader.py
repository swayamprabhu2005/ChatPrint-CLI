"""MHTML multipart MIME reader using Python's standard email package."""

import email
from dataclasses import dataclass, field
from email.message import Message
from pathlib import Path

from bs4 import BeautifulSoup

from chatprint.errors import InvalidInputError, MHTMLParseError


@dataclass
class MHTMLDocument:
    """Represents an unpacked MHTML document."""

    raw_html: str
    file_path: Path
    title: str = ""
    resources: dict[str, bytes] = field(default_factory=dict)
    resource_types: dict[str, str] = field(default_factory=dict)
    snapshot_location: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def soup(self) -> BeautifulSoup:
        """Parse and return a BeautifulSoup DOM tree."""
        return BeautifulSoup(self.raw_html, "html.parser")


def read_mhtml_file(file_path: Path) -> MHTMLDocument:
    """Parse an MHTML file and extract its primary HTML document and embedded resources.

    Args:
        file_path: Path to .mhtml or .mht file.

    Returns:
        MHTMLDocument containing root HTML and resources.

    Raises:
        InvalidInputError: If file cannot be read.
        MHTMLParseError: If file is not valid MHTML or contains no HTML body.
    """
    path = Path(file_path)
    try:
        raw_bytes = path.read_bytes()
    except OSError as e:
        raise InvalidInputError(
            f"Failed to read MHTML file: {path} ({e})",
            suggestion="Check file permissions and path.",
        ) from e

    if not raw_bytes.strip():
        raise MHTMLParseError(
            f"The MHTML file is empty: {path.name}",
            suggestion="Verify that the webpage was saved properly.",
        )

    # Strip UTF-8 BOM if present – some editors/tools prepend it, which
    # confuses Python's email MIME parser.
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        raw_bytes = raw_bytes[3:]

    try:
        msg: Message = email.message_from_bytes(raw_bytes)
    except Exception as e:
        raise MHTMLParseError(
            f"Failed to parse MHTML structure in: {path.name} ({e})",
            suggestion="Confirm the file is a valid MHTML snapshot.",
        ) from e

    snapshot_location = (
        msg.get("Snapshot-Content-Location")
        or msg.get("Content-Location")
        or ""
    )

    primary_html: str | None = None
    resources: dict[str, bytes] = {}
    resource_types: dict[str, str] = {}

    for part in msg.walk():
        content_type = part.get_content_type().lower()
        payload = part.get_payload(decode=True)
        if payload is None:
            continue

        location = part.get("Content-Location") or ""
        content_id = part.get("Content-ID") or ""
        if content_id:
            # Clean enclosing brackets <cid:xyz> or <xyz>
            content_id = content_id.strip("<>")
            if not content_id.startswith("cid:"):
                content_id = f"cid:{content_id}"

        # Register resource under both location and CID if present
        if location:
            resources[location] = payload
            resource_types[location] = content_type
        if content_id:
            resources[content_id] = payload
            resource_types[content_id] = content_type

        # Check if this part is the primary HTML
        if content_type == "text/html" and primary_html is None:
            charset = part.get_content_charset() or "utf-8"
            try:
                primary_html = payload.decode(charset)
            except (UnicodeDecodeError, LookupError):
                try:
                    primary_html = payload.decode("utf-8")
                except UnicodeDecodeError:
                    primary_html = payload.decode("latin1", errors="replace")

    # If message wasn't multipart or walk didn't find text/html part
    if primary_html is None and msg.get_content_type().lower() == "text/html":
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                primary_html = payload.decode(charset)
            except (UnicodeDecodeError, LookupError):
                primary_html = payload.decode("utf-8", errors="replace")

    if not primary_html or not primary_html.strip():
        raise MHTMLParseError(
            f"No HTML document found inside MHTML snapshot: {path.name}",
            suggestion="Ensure the file was saved as 'Single File' or MHTML from a browser.",
        )

    # Validate that primary_html actually contains HTML markup
    lower_html = primary_html.lower()
    if not ("<html" in lower_html or "<body" in lower_html or "<!doctype html" in lower_html or "<div" in lower_html):
        raise MHTMLParseError(
            f"MHTML payload does not contain valid HTML document: {path.name}",
            suggestion="Ensure the file is a valid MHTML snapshot containing webpage HTML.",
        )

    # Extract page title and meta
    soup = BeautifulSoup(primary_html, "html.parser")
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    metadata: dict[str, str] = {
        "subject": msg.get("Subject", ""),
        "date": msg.get("Date", ""),
        "snapshot_location": snapshot_location,
    }
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property")
        content = meta.get("content")
        if name and content:
            metadata[name] = content

    return MHTMLDocument(
        raw_html=primary_html,
        file_path=path,
        title=title,
        resources=resources,
        resource_types=resource_types,
        snapshot_location=snapshot_location,
        metadata=metadata,
    )
