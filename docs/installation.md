# Installation & Setup Guide

This guide covers all methods to install, configure, and verify **AI Conversation CLI**.

---

## System Requirements

- **Operating System**: Windows 10/11, macOS 11+, or modern Linux (Ubuntu 20.04+, Debian 11+, Fedora 36+, Arch Linux).
- **Target Runtime**: Python 3.10.8 (Compatible with Python 3.10, 3.11, 3.12).
- **Network**: Internet connection required *only* during initial package installation. Conversions operate 100% offline.

---

## Method 1: Install with pipx (Recommended)

`pipx` installs Python CLI tools into isolated virtual environments and exposes their executable globally.

```bash
# If pipx is not installed:
# Windows: winget install pipx
# macOS: brew install pipx
# Linux: sudo apt install pipx

pipx install git+https://github.com/swayamprabhu2005/AI-Conversation-CLI.git
```

To upgrade in the future:
```bash
pipx upgrade ai-conversation
```

---

## Method 2: Bootstrap Setup Scripts

The repository includes platform-specific bootstrap scripts that check your system, ensure Python 3.10.8 is present (or offer to install it into a private application runtime), and register the CLI on your PATH.

### Windows (PowerShell)
Open PowerShell and run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\install-windows.ps1
```
The installer:
1. Verifies system architecture (x64 / arm64).
2. Looks for Python 3.10.8. If missing, requests consent to download official `python-3.10.8-amd64.exe` from `python.org`.
3. Verifies SHA-256 cryptographic checksum against official release:
   `6b896b0fd01e8cffadcf2fd75a9fe847248e5828ae8f92167812ec1e57c6b90f`
4. Prompts for an installation directory (default: `%LOCALAPPDATA%\AIConversationCLI`).
5. Creates a private virtual environment and installs the CLI.
6. Registers the executable to your User `PATH`.
7. Runs `ai-conversation doctor` to confirm readiness.

### Linux (Bash)
```bash
chmod +x scripts/install-linux.sh
./scripts/install-linux.sh
```

### macOS (Terminal)
```bash
chmod +x scripts/install-macos.sh
./scripts/install-macos.sh
```

---

## Method 3: Developer Installation from Source

```bash
git clone https://github.com/swayamprabhu2005/AI-Conversation-CLI.git
cd AI-Conversation-CLI

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -e ".[dev]"
```

Verify installation:
```bash
ai-conversation --version
ai-conversation doctor
```
