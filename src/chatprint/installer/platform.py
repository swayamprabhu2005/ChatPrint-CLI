"""Platform and hardware architecture detection."""

import platform
import sys
from dataclasses import dataclass


@dataclass
class PlatformInfo:
    """System platform and architecture details."""

    system: str  # 'windows', 'macos', 'linux'
    release: str
    machine: str  # 'x86_64', 'arm64', 'AMD64', etc.
    is_64bit: bool
    arch_normalized: str  # 'x64', 'arm64', 'x86'


def get_platform_info() -> PlatformInfo:
    """Identify the current operating system and CPU architecture."""
    system_raw = platform.system().lower()
    if system_raw == "darwin":
        system = "macos"
    elif system_raw == "windows":
        system = "windows"
    else:
        system = "linux"

    machine = platform.machine()
    is_64bit = sys.maxsize > 2**32

    # Normalize architecture string
    machine_lower = machine.lower()
    if machine_lower in ("amd64", "x86_64", "x64"):
        arch_normalized = "x64"
    elif machine_lower in ("arm64", "aarch64"):
        arch_normalized = "arm64"
    else:
        arch_normalized = "x86" if not is_64bit else "x64"

    return PlatformInfo(
        system=system,
        release=platform.release(),
        machine=machine,
        is_64bit=is_64bit,
        arch_normalized=arch_normalized,
    )
