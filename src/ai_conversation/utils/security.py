"""Security utilities for untrusted input handling and sandbox containment."""

import re
from pathlib import Path

from ai_conversation.errors import InvalidInputError

_UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize_filename(name: str, fallback: str = "conversation") -> str:
    """Sanitize an untrusted filename to prevent path traversal or invalid characters.

    Args:
        name: Raw filename or title string.
        fallback: Safe fallback name if sanitization produces empty string.

    Returns:
        Clean, safe filename.
    """
    # Remove path components like ../ or ..\
    clean = re.sub(r"(\.\.[/\\])+", "", name)
    clean = _UNSAFE_FILENAME_CHARS.sub("_", clean)
    clean = clean.strip(". _").strip()
    if not clean:
        clean = fallback
    # Limit length
    if len(clean) > 120:
        clean = clean[:120].rstrip()
    return clean


def ensure_safe_path(base_dir: Path, target_path: Path) -> Path:
    """Ensure target_path is contained within base_dir to prevent path traversal.

    Args:
        base_dir: Directory that must contain target_path.
        target_path: Path to validate.

    Returns:
        Resolved safe path.

    Raises:
        InvalidInputError: If path traversal is detected.
    """
    resolved_base = base_dir.resolve()
    resolved_target = target_path.resolve()

    try:
        resolved_target.relative_to(resolved_base)
    except ValueError as e:
        raise InvalidInputError(
            f"Path traversal detected: {target_path} is outside {base_dir}"
        ) from e

    return resolved_target
