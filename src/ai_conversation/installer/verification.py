"""System self-diagnostic and health check engine for 'ai-conversation doctor'."""

import shutil
from dataclasses import dataclass

from ai_conversation.installer.paths import get_default_install_dir, validate_install_dir
from ai_conversation.installer.platform import get_platform_info
from ai_conversation.installer.python_runtime import check_python_version


@dataclass
class DiagnosticCheck:
    """A single diagnostic check item."""

    name: str
    status: bool
    message: str
    details: str = ""


@dataclass
class DoctorReport:
    """Overall diagnostic report."""

    checks: list[DiagnosticCheck]
    all_ok: bool


def run_doctor_check() -> DoctorReport:
    """Perform comprehensive system diagnostics.

    Returns:
        DoctorReport containing individual checks and aggregate status.
    """
    checks: list[DiagnosticCheck] = []

    # 1. Python version check
    py_info = check_python_version()
    if py_info.is_exact_match:
        checks.append(
            DiagnosticCheck(
                name="Python",
                status=True,
                message=f"{py_info.version_string} (exact target 3.10.8)",
            )
        )
    elif py_info.is_supported:
        checks.append(
            DiagnosticCheck(
                name="Python",
                status=True,
                message=f"{py_info.version_string} (compatible >=3.10)",
            )
        )
    else:
        checks.append(
            DiagnosticCheck(
                name="Python",
                status=False,
                message=f"{py_info.version_string} (unsupported, target 3.10.8)",
            )
        )

    # 2. Platform & Architecture
    plat = get_platform_info()
    checks.append(
        DiagnosticCheck(
            name="Platform",
            status=True,
            message=f"{plat.system.capitalize()} {plat.arch_normalized} ({plat.machine})",
        )
    )

    # 3. Installation directory writability
    default_dir = get_default_install_dir()
    is_writable, reason = validate_install_dir(default_dir)
    checks.append(
        DiagnosticCheck(
            name="Installation",
            status=is_writable,
            message=f"OK ({default_dir})" if is_writable else f"Failed: {reason}",
        )
    )

    # 4. PDF Engine (ReportLab Platypus) check
    try:
        import reportlab
        checks.append(
            DiagnosticCheck(
                name="PDF engine",
                status=True,
                message=f"ReportLab {reportlab.__version__} OK",
            )
        )
    except Exception as e:
        checks.append(
            DiagnosticCheck(
                name="PDF engine",
                status=False,
                message=f"ReportLab unavailable: {e}",
            )
        )

    # 5. Core dependencies check
    deps = ["click", "rich", "bs4", "reportlab", "platformdirs", "pypdf"]
    missing = []
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)

    if not missing:
        checks.append(
            DiagnosticCheck(
                name="Dependencies",
                status=True,
                message="All core packages verified",
            )
        )
    else:
        checks.append(
            DiagnosticCheck(
                name="Dependencies",
                status=False,
                message=f"Missing: {', '.join(missing)}",
            )
        )

    # 6. CLI PATH availability
    cli_on_path = shutil.which("ai-conversation") is not None
    checks.append(
        DiagnosticCheck(
            name="CLI PATH",
            status=bool(cli_on_path),
            message="Executable on PATH" if cli_on_path else "Not found on PATH (run via python -m ai_conversation or install)",
        )
    )

    all_ok = all(c.status for c in checks if c.name != "CLI PATH")
    return DoctorReport(checks=checks, all_ok=all_ok)
