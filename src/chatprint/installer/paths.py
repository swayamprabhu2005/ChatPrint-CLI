"""Installation directory resolution and validation."""

import os
from pathlib import Path

from chatprint.installer.platform import get_platform_info


def get_default_install_dir() -> Path:
    """Return the platform-appropriate default installation directory.

    Windows: %LOCALAPPDATA%\\ChatPrintCLI
    macOS: ~/Library/Application Support/ChatPrintCLI
    Linux: ~/.local/share/chatprint-cli
    """
    platform_info = get_platform_info()
    home = Path.home()

    if platform_info.system == "windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "ChatPrintCLI"
        return home / "AppData" / "Local" / "ChatPrintCLI"

    if platform_info.system == "macos":
        return home / "Library" / "Application Support" / "ChatPrintCLI"

    return home / ".local" / "share" / "chatprint-cli"


def validate_install_dir(target_dir: Path) -> tuple[bool, str]:
    """Validate that the given path is safe and writable for application installation.

    Args:
        target_dir: Path proposed for installation.

    Returns:
        Tuple of (is_valid: bool, reason_message: str).
    """
    path = Path(target_dir).resolve()

    # Disallow root or dangerous system directories
    str_path = str(path).lower()
    disallowed_prefixes = [
        "c:\\windows",
        "c:\\program files",
        "/bin",
        "/sbin",
        "/usr/bin",
        "/usr/sbin",
        "/etc",
        "/root",
    ]
    for disallowed in disallowed_prefixes:
        if str_path == disallowed or str_path.startswith(disallowed + os.sep):
            return False, f"Cannot install into protected system directory: {path}"

    # Test directory creation and write permission
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
    except Exception as e:
        return False, f"Directory is not writable: {e}"

    return True, "Directory is valid and writable."
