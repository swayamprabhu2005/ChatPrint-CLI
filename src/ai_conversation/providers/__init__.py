"""Provider registry and automatic source detection engine."""

from typing import Any

from bs4 import BeautifulSoup

from ai_conversation.errors import ProviderDetectionError
from ai_conversation.providers.base import ConversationProvider
from ai_conversation.providers.chatgpt import ChatGPTProvider
from ai_conversation.providers.gemini import GeminiProvider
from ai_conversation.providers.generic import GenericProvider

AVAILABLE_PROVIDERS: dict[str, ConversationProvider] = {
    "gemini": GeminiProvider(),
    "chatgpt": ChatGPTProvider(),
    "generic": GenericProvider(),
}


def get_provider(name: str) -> ConversationProvider:
    """Retrieve a registered provider by name.

    Args:
        name: Provider name ('gemini', 'chatgpt', 'generic').

    Returns:
        ConversationProvider instance.

    Raises:
        ProviderDetectionError: If name is unknown.
    """
    key = name.strip().lower()
    if key in AVAILABLE_PROVIDERS:
        return AVAILABLE_PROVIDERS[key]
    raise ProviderDetectionError(
        f"Unknown provider '{name}' specified.",
        suggestion=f"Available providers: {', '.join(AVAILABLE_PROVIDERS.keys())}, or use 'auto'.",
    )


def detect_best_provider(
    soup: BeautifulSoup,
    raw_html: str,
    metadata: dict[str, Any],
) -> tuple[ConversationProvider, float]:
    """Score all registered providers and select the one with highest confidence.

    Args:
        soup: Parsed BeautifulSoup DOM.
        raw_html: Raw HTML string.
        metadata: Document metadata.

    Returns:
        Tuple of (selected ConversationProvider, confidence float score).
    """
    scores: list[tuple[float, ConversationProvider]] = []

    for provider in (GeminiProvider(), ChatGPTProvider()):
        conf = provider.detect_confidence(soup, raw_html, metadata)
        scores.append((conf, provider))

    scores.sort(key=lambda x: x[0], reverse=True)
    best_score, best_provider = scores[0]

    # If confidence is too low (< 0.25), use Generic fallback
    if best_score < 0.25:
        generic = GenericProvider()
        return generic, generic.detect_confidence(soup, raw_html, metadata)

    return best_provider, best_score
