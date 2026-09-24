"""Unit tests for security, sandbox containment, and filename sanitization."""

from pathlib import Path

import pytest

from ai_conversation.errors import InvalidInputError
from ai_conversation.utils.security import ensure_safe_path, sanitize_filename


def test_sanitize_filename():
    assert sanitize_filename("safe_title") == "safe_title"
    assert sanitize_filename('bad/title:with"special?chars*') == "bad_title_with_special_chars"
    assert sanitize_filename("../../etc/passwd") == "etc_passwd"
    assert sanitize_filename("") == "conversation"


def test_ensure_safe_path(tmp_path: Path):
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()

    safe_target = sandbox / "sub" / "file.txt"
    resolved = ensure_safe_path(sandbox, safe_target)
    assert resolved == safe_target.resolve()

    traversal_target = sandbox / ".." / "outside.txt"
    with pytest.raises(InvalidInputError, match="Path traversal"):
        ensure_safe_path(sandbox, traversal_target)
