"""Base interface for AI conversation providers."""

from abc import ABC, abstractmethod
from typing import Any

from bs4 import BeautifulSoup

from chatprint.models import Conversation


class ConversationProvider(ABC):
    """Abstract base class for source-specific conversation providers."""

    name: str = "base"
    display_name: str = "Base Provider"

    @abstractmethod
    def detect_confidence(
        self,
        soup: BeautifulSoup,
        raw_html: str,
        metadata: dict[str, Any],
    ) -> float:
        """Evaluate the confidence (0.0 to 1.0) that the document is from this provider.

        Args:
            soup: Parsed BeautifulSoup DOM.
            raw_html: Raw HTML string.
            metadata: Extracted header or document metadata.

        Returns:
            Float confidence score between 0.0 and 1.0.
        """

    @abstractmethod
    def extract(
        self,
        soup: BeautifulSoup,
        resources: dict[str, bytes],
        original_filename: str,
    ) -> Conversation:
        """Extract conversation turns and produce a normalized Conversation model.

        Args:
            soup: Parsed BeautifulSoup DOM.
            resources: Extracted embedded resources (images, etc.).
            original_filename: Name of the input file.

        Returns:
            Normalized Conversation instance.
        """
