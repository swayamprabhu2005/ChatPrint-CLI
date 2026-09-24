"""Cross-platform installer and Python 3.10.8 runtime bootstrapper."""

from ai_conversation.installer.paths import get_default_install_dir, validate_install_dir
from ai_conversation.installer.platform import PlatformInfo, get_platform_info
from ai_conversation.installer.python_runtime import (
    PythonRuntimeInfo,
    check_python_version,
    verify_checksum,
)
from ai_conversation.installer.verification import run_doctor_check

__all__ = [
    "PlatformInfo",
    "PythonRuntimeInfo",
    "check_python_version",
    "get_default_install_dir",
    "get_platform_info",
    "run_doctor_check",
    "validate_install_dir",
    "verify_checksum",
]
