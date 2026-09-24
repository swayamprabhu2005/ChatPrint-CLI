"""Normalized data models for AI conversations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Role(str, Enum):
    """Conversation participant role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ContentBlock:
    """Base class for structured message content blocks."""


@dataclass
class ParagraphBlock(ContentBlock):
    """A standard text paragraph."""

    text: str


@dataclass
class HeadingBlock(ContentBlock):
    """A heading element with specified level (1-6)."""

    level: int
    text: str


@dataclass
class ListBlock(ContentBlock):
    """An ordered or unordered list of items."""

    items: list[str]
    ordered: bool = False


@dataclass
class CodeBlock(ContentBlock):
    """A formatted code block with optional syntax language."""

    code: str
    language: str = ""


@dataclass
class TableBlock(ContentBlock):
    """A structured tabular data block."""

    headers: list[str]
    rows: list[list[str]]


@dataclass
class CitationBlock(ContentBlock):
    """A citation or reference link from an assistant response."""

    text: str
    url: str | None = None


@dataclass
class ImageBlock(ContentBlock):
    """An embedded image attachment."""

    data: bytes
    mime_type: str = "image/png"
    caption: str = ""


@dataclass
class Message:
    """A single turn in the conversation."""

    role: Role
    blocks: list[ContentBlock] = field(default_factory=list)
    order: int = 0
    timestamp: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def plain_text(self) -> str:
        """Extract plain text representation of all blocks in the message."""
        parts: list[str] = []
        for block in self.blocks:
            if isinstance(block, (ParagraphBlock, HeadingBlock)):
                parts.append(block.text)
            elif isinstance(block, ListBlock):
                prefix = "1. " if block.ordered else "• "
                parts.extend(f"{prefix}{item}" for item in block.items)
            elif isinstance(block, CodeBlock):
                parts.append(block.code)
            elif isinstance(block, TableBlock):
                if block.headers:
                    parts.append(" | ".join(block.headers))
                for row in block.rows:
                    parts.append(" | ".join(row))
            elif isinstance(block, CitationBlock):
                parts.append(f"[{block.text}]({block.url})" if block.url else f"[{block.text}]")
        return "\n\n".join(parts)


@dataclass
class Conversation:
    """Complete multi-turn conversation model."""

    title: str
    source: str
    original_filename: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    messages: list[Message] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def user_messages_count(self) -> int:
        """Count of user turns."""
        return sum(1 for m in self.messages if m.role == Role.USER)

    @property
    def assistant_messages_count(self) -> int:
        """Count of assistant turns."""
        return sum(1 for m in self.messages if m.role == Role.ASSISTANT)

    @property
    def total_messages_count(self) -> int:
        """Total number of messages."""
        return len(self.messages)


@dataclass
class ExtractionResult:
    """Result of conversation extraction and analysis."""

    conversation: Conversation
    confidence: float
    detected_provider: str
    stats: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    candidate_info: dict[str, Any] = field(default_factory=dict)
