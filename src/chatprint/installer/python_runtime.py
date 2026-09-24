"""Python 3.10.8 runtime detection, cryptographic verification, and provisioning metadata."""

import hashlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

TARGET_PYTHON_VERSION = (3, 10, 8)
TARGET_PYTHON_STR = "3.10.8"

# Official Python 3.10.8 Release Artifacts and SHA-256 Checksums
# Source: https://www.python.org/downloads/release/python-3108/
OFFICIAL_PYTHON_RELEASES = {
    ("windows", "x64"): {
        "filename": "python-3.10.8-amd64.exe",
        "url": "https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe",
        "sha256": "6b896b0fd01e8cffadcf2fd75a9fe847248e5828ae8f92167812ec1e57c6b90f",
    },
    ("windows", "arm64"): {
        "filename": "python-3.10.8-arm64.exe",
        "url": "https://www.python.org/ftp/python/3.10.8/python-3.10.8-arm64.exe",
        "sha256": "2a98f121d423910900b95764dca6e1a4ec89fae0cfadff3e602e1c39050074b1",
    },
    ("macos", "universal"): {
        "filename": "python-3.10.8-macos11.pkg",
        "url": "https://www.python.org/ftp/python/3.10.8/python-3.10.8-macos11.pkg",
        "sha256": "2b1a8d052a70cb6531390f7f07096d29ea76c0293ecae8c9a35e72d242634d28",
    },
    ("source", "tar"): {
        "filename": "Python-3.10.8.tar.xz",
        "url": "https://www.python.org/ftp/python/3.10.8/Python-3.10.8.tar.xz",
        "sha256": "6a30ecdeaf8888730bb53f0305412ec8c9f686da3b199155257e5d896426fa74",
    },
}


@dataclass
class PythonRuntimeInfo:
    """Information about an inspected Python runtime."""

    executable: Path
    version_tuple: tuple[int, int, int]
    version_string: str
    is_exact_match: bool
    is_supported: bool


def verify_checksum(file_path: Path, expected_sha256: str) -> bool:
    """Compute the SHA-256 hash of a file and verify against expected hash.

    Args:
        file_path: Path to the downloaded file.
        expected_sha256: Hex string of expected SHA-256 digest.

    Returns:
        True if checksum matches, False otherwise.
    """
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    actual = hasher.hexdigest().lower()
    return actual == expected_sha256.lower()


def check_python_version(executable: Path | None = None) -> PythonRuntimeInfo:
    """Inspect current or specified Python interpreter version.

    Args:
        executable: Optional path to Python binary. Defaults to sys.executable.

    Returns:
        PythonRuntimeInfo instance.
    """
    if executable is None:
        exe_path = Path(sys.executable)
        v = sys.version_info
        v_tuple = (v.major, v.minor, v.micro)
        v_str = f"{v.major}.{v.minor}.{v.micro}"
    else:
        exe_path = Path(executable)
        try:
            result = subprocess.run(
                [str(exe_path), "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            v_str = result.stdout.strip()
            parts = [int(p) for p in v_str.split(".")]
            v_tuple = (parts[0], parts[1], parts[2])
        except Exception:
            v_str = "unknown"
            v_tuple = (0, 0, 0)

    is_exact = v_tuple == TARGET_PYTHON_VERSION
    is_supported = (v_tuple[0] == 3 and v_tuple[1] >= 10)

    return PythonRuntimeInfo(
        executable=exe_path,
        version_tuple=v_tuple,
        version_string=v_str,
        is_exact_match=is_exact,
        is_supported=is_supported,
    )
