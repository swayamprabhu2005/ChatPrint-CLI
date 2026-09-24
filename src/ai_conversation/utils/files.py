"""File handling and output path resolution utilities."""

import tempfile
from pathlib import Path


def get_unique_numbered_path(target: Path) -> Path:
    """Generate a unique path by adding incrementing numerical suffixes if file exists.

    Example:
        chat.pdf -> chat-1.pdf -> chat-2.pdf
    """
    if not target.exists():
        return target

    parent = target.parent
    stem = target.stem
    suffix = target.suffix

    counter = 1
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def resolve_output_pdf_path(
    input_file: Path,
    output_dir: Path | None = None,
    output_file: Path | None = None,
    force: bool = False,
) -> Path:
    """Determine the final destination path for the generated PDF.

    Args:
        input_file: Source file path.
        output_dir: Optional custom destination directory.
        output_file: Optional explicit target file path.
        force: If True, allow overwriting existing files without incrementing suffix.

    Returns:
        Safe destination Path.
    """
    if output_file:
        dest = output_file.resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and not force:
            dest = get_unique_numbered_path(dest)
        return dest

    default_name = f"{input_file.stem}.pdf"
    if output_dir:
        target_dir = output_dir.resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / default_name
    else:
        dest = input_file.parent.resolve() / default_name

    if dest.exists() and not force:
        dest = get_unique_numbered_path(dest)

    return dest


class TempSandbox:
    """Context manager for temporary file extraction with guaranteed cleanup."""

    def __init__(self, prefix: str = "ai_conv_"):
        self._temp_dir = tempfile.TemporaryDirectory(prefix=prefix)
        self.path = Path(self._temp_dir.name)

    def __enter__(self) -> Path:
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._temp_dir.cleanup()
