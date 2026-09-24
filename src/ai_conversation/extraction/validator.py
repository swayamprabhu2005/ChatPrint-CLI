"""Validation rules for extracted conversation models."""

from ai_conversation.errors import ConversationExtractionError
from ai_conversation.models import Conversation, Role

_OBVIOUS_UI_STRINGS = [
    "sign in",
    "google apps",
    "privacy & terms",
    "settings",
    "search tools",
    "new chat",
    "upgrade to plus",
]


def validate_conversation(conversation: Conversation, confidence: float = 1.0) -> list[str]:
    """Validate that the extracted conversation is non-empty and structurally sound.

    Args:
        conversation: Extracted Conversation object.
        confidence: Detection/extraction confidence score.

    Returns:
        List of warning strings if any issues are detected.

    Raises:
        ConversationExtractionError: If the conversation is invalid or empty.
    """
    warnings: list[str] = []

    if not conversation.messages:
        raise ConversationExtractionError(
            "No conversation messages could be extracted from the document.",
            suggestion="Verify the saved file contains the conversation and try specifying --source gemini or --source chatgpt.",
        )

    # Check that there is meaningful text across messages
    total_text = " ".join(msg.plain_text for msg in conversation.messages).strip()
    if not total_text or len(total_text) < 10:
        raise ConversationExtractionError(
            "Extracted conversation content is empty or trivially short.",
            suggestion="Check if the webpage was fully loaded before saving.",
        )

    # Check if content is exclusively navigation strings
    lower_text = total_text.lower()
    ui_matches = sum(1 for s in _OBVIOUS_UI_STRINGS if s in lower_text)
    if ui_matches >= 4 and len(total_text) < 150:
        raise ConversationExtractionError(
            "Extracted content appears to be webpage navigation rather than an AI conversation.",
            suggestion="Try specifying the source explicitly using --source gemini or --source chatgpt.",
        )

    # Plausibility checks
    user_turns = sum(1 for m in conversation.messages if m.role == Role.USER)
    assistant_turns = sum(1 for m in conversation.messages if m.role == Role.ASSISTANT)

    if user_turns == 0 and assistant_turns == 0:
        warnings.append("No distinct user or assistant role markers could be identified.")

    if confidence < 0.6:
        warnings.append(
            f"Extraction confidence is low ({int(confidence * 100)}%). "
            "Some conversation formatting might need manual verification."
        )

    return warnings
