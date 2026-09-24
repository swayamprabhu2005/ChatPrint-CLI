"""Unit tests for installer helpers, Python runtime verification, and diagnostics."""

import hashlib
from pathlib import Path

from ai_conversation.installer.paths import get_default_install_dir, validate_install_dir
from ai_conversation.installer.platform import get_platform_info
from ai_conversation.installer.python_runtime import (
    check_python_version,
    verify_checksum,
)
from ai_conversation.installer.verification import run_doctor_check


def test_platform_info():
    info = get_platform_info()
    assert info.system in ("windows", "macos", "linux")
    assert info.arch_normalized in ("x64", "arm64", "x86")
    assert info.is_64bit is True or info.is_64bit is False


def test_python_runtime_check():
    info = check_python_version()
    assert info.executable.exists()
    assert info.is_supported is True


def test_checksum_verification(tmp_path: Path):
    test_file = tmp_path / "test.bin"
    content = b"AI Conversation CLI secure content"
    test_file.write_bytes(content)

    expected_sha256 = hashlib.sha256(content).hexdigest()
    assert verify_checksum(test_file, expected_sha256) is True
    assert verify_checksum(test_file, "bad_hash_000000000000000000000000000000000000") is False


def test_default_install_dir():
    dir_path = get_default_install_dir()
    assert "AIConversationCLI" in str(dir_path) or "ai-conversation" in str(dir_path)


def test_validate_install_dir(tmp_path: Path):
    custom_dir = tmp_path / "CustomAppDir"
    valid, _ = validate_install_dir(custom_dir)
    assert valid is True

    # Test protected system directory rejection
    bad_dir = Path("C:/Windows/System32")
    valid_bad, _ = validate_install_dir(bad_dir)
    assert valid_bad is False


def test_doctor_diagnostic():
    report = run_doctor_check()
    assert len(report.checks) >= 5
    # Python, Platform, Dependencies, PDF engine should be present
    check_names = [c.name for c in report.checks]
    assert "Python" in check_names
    assert "Platform" in check_names
    assert "PDF engine" in check_names
    assert "Dependencies" in check_names
