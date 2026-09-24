"""Custom exceptions for AI Conversation CLI."""


class AIConversationError(Exception):
    """Base exception for all AI Conversation CLI errors."""

    def __init__(self, message: str, suggestion: str | None = None):
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion


class InvalidInputError(AIConversationError):
    """Raised when an input file does not exist or is inaccessible."""


class UnsupportedFormatError(AIConversationError):
    """Raised when the input format is not recognized or unsupported."""


class MHTMLParseError(AIConversationError):
    """Raised when parsing MHTML multipart MIME structure fails."""


class ProviderDetectionError(AIConversationError):
    """Raised when the source provider cannot be determined with sufficient confidence."""


class ConversationExtractionError(AIConversationError):
    """Raised when conversation turns cannot be extracted or are invalid."""


class PDFGenerationError(AIConversationError):
    """Raised when rendering or writing the output PDF fails."""


class InstallerError(AIConversationError):
    """Raised when setup or runtime provisioning fails."""
