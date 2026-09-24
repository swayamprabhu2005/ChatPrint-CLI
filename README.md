# ChatPrint CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)]()

Convert locally saved ChatPrint webpages (**Google Gemini AI Mode** and **ChatGPT**) into clean, readable, professional, searchable PDFs.

---

## Overview

Modern web browsers allow saving webpages locally (e.g., using `Ctrl + S` and selecting **"Single File"** or **"Webpage, Complete"**), creating `.mhtml`, `.mht`, or `.html` files.

However, saved conversation pages from Google Gemini and ChatGPT are cluttered with search bars, user account chips, recommendation sidebars, feedback buttons, and browser chrome.

**ChatPrint CLI** parses these locally saved files offline, extracts the complete conversation turns from beginning to end, removes all irrelevant website UI, and generates a polished, vector-text PDF suitable for archiving, printing, and sharing.

```
Saved Webpage (.mhtml / .html)
             │
             ▼
   chatprint convert
             │
             ▼
Clean, Searchable, Professional PDF
```

---

## Key Features

- **100% Offline & Private**: Operates entirely on locally saved files. No API keys, no Google/ChatGPT account access, no live scraping, and zero telemetry.
- **First-Class MHTML Support**: Full MIME multipart parsing using Python's standard `email` module to extract HTML, embedded images, and stylesheets.
- **Provider-Specific Clean Extraction**:
  - **Google Gemini AI Mode**: Extracts multi-turn questions and AI responses; removes Google headers, search tabs, account profile chips, right sidebars (`#rhs`), "People also ask", and footer links.
  - **ChatGPT**: Extracts user prompts and assistant turns; removes navigation sidebars, model dropdowns, feedback/copy buttons, and disclaimers.
  - **Generic Fallback**: Heuristic conversational turn extractor for unknown AI chat pages.
- **Resilient Layered Heuristics**: Does not rely on a single fragile CSS class name. Analyzes semantic structures, turn order, and content density.
- **High-Quality Vector PDFs**: Built with ReportLab Platypus. Produces searchable, selectable text with dynamic page numbering ("Page X of Y"), syntax-styled code blocks, formatted tables, and distinct user vs assistant styling.
- **Cross-Platform**: Tested on Windows, macOS, and Linux.
- **Safe Output Handling**: Prevents accidental overwrites by default (`chat.pdf` $\rightarrow$ `chat-1.pdf`), with `--force` override option.

---

## Supported AI Sources & Formats

| Source | Input Formats | Features Extracted |
| :--- | :--- | :--- |
| **Google Gemini AI Mode** | `.mhtml`, `.mht`, `.html`, `.htm` | User query, AI Overview, follow-up turns, headings, bullet lists, code, tables |
| **ChatGPT** | `.mhtml`, `.mht`, `.html`, `.htm` | Multi-turn user/assistant dialogue, markdown text, code blocks, tables |
| **Generic AI Webpage** | `.html`, `.htm`, `.mhtml` | Heuristic article / dialogue turn parsing fallback |

---

## Prerequisites

| Requirement | Needed? | Details |
| :--- | :---: | :--- |
| **Operating System** | Yes | Windows 10/11, macOS 11+, or modern Linux |
| **PowerShell / Terminal** | Yes | Built into Windows (PowerShell), macOS (Terminal), and Linux (Bash) |
| **Python** | Automatic | If Python 3.10+ is detected, it is reused. If missing, the Windows installer can automatically download and provision official Python 3.10.8 safely into a private app directory. |
| **Git** | **No** | Not required for end-users. You can download the project ZIP directly from GitHub. |
| **Internet during conversion** | **No** | Conversions operate 100% locally and offline without external API keys or network requests. |

---

## Installation

### Option 1: Install Without Git (Download ZIP - Recommended for End Users)
If you do not have Git installed on your computer:
1. Open this repository on GitHub in your web browser:
   `https://github.com/swayamprabhu2005/chatprint-CLI`
2. Click the green **`<> Code`** button near the top right, then click **`Download ZIP`**.
3. Extract the downloaded `.zip` file to any temporary folder (e.g. your Downloads folder).
4. Run the installer for your operating system:
   - **Windows**:
     - **Option A (Easiest - Command Prompt or Double-Click)**:
       Simply double-click **`install.bat`** in the folder, or in Command Prompt (`cmd.exe`) run:
       ```cmd
       install.bat
       ```
     - **Option B (PowerShell)**:
       Open PowerShell inside the extracted folder and run:
       ```powershell
       powershell -ExecutionPolicy Bypass -File .\scripts\install-windows.ps1
       ```
       *(or right-click `scripts\install-windows.ps1` and choose **"Run with PowerShell"**)*
   - **macOS (Terminal)**:
     ```bash
     chmod +x scripts/install-macos.sh
     ./scripts/install-macos.sh
     ```
   - **Linux (Bash)**:
     ```bash
     chmod +x scripts/install-linux.sh
     ./scripts/install-linux.sh
     ```
5. **How the Setup Progresses**:
   - **Step 1 - Python Verification**: The script checks if Python 3.10.8 is present. If missing, it asks:
     `Download official Python 3.10.8 installer from python.org? [Y/n]`
     Selecting `Y` downloads the official installer, verifies its SHA-256 cryptographic checksum, and installs Python into a private application folder without touching your system's global settings.
   - **Step 2 - Installation Folder**: The installer asks where to place the application:
     `Where would you like to install ChatPrint CLI?`
     `Default: C:\Users\<Username>\AppData\Local\ChatPrintCLI`
     Press **Enter** to accept the default, or type any custom location (e.g. `D:\Tools\ChatPrintCLI`).
   - **Step 3 - PATH Registration**: The installer adds the executable to your user `PATH`.
   - **Step 4 - Verification**: It runs `chatprint doctor` to verify system readiness.
6. Once complete, you can safely delete the extracted `.zip` folder. The application is permanently installed and ready to run from any terminal!

### Option 2: Install via pipx (For Users with Python & pipx)
```bash
pipx install git+https://github.com/swayamprabhu2005/chatprint-CLI.git
```

### Option 3: Developer Installation from Source
> [!NOTE]
> This option is intended for developers contributing to the codebase. End-users do not need to run this.

```bash
git clone https://github.com/swayamprabhu2005/chatprint-CLI.git
cd chatprint-CLI

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"
```

---

## Quick Start

### 1. Save an ChatPrint Webpage
1. Open Google Gemini or ChatGPT in your browser (Chrome, Edge, Brave, Firefox).
2. Save the webpage locally:
   - In Chrome/Edge: Press `Ctrl + S` (or `Cmd + S` on macOS).
   - In the **"Save as type"** dropdown, select **"Webpage, Single File (*.mhtml)"** or **"Webpage, Complete (*.htm, *.html)"**.
3. Save the file (e.g. `conversation.mhtml`).

### 2. Convert to PDF
```bash
chatprint convert "C:\Users\User\Downloads\conversation.mhtml"
```

**Terminal Output:**
```text
ChatPrint CLI
────────────────────────────────────────
Input: conversation.mhtml
Format: MHTML
[1/4] Reading saved webpage...
[2/4] Detecting conversation source...
Source: Google Gemini AI Mode
[3/4] Extracting conversation & cleaning UI...
[4/4] Generating PDF...

✓ PDF generated successfully

Output:
C:\Users\User\Downloads\conversation.pdf
```

---

## CLI Usage & Commands

### `chatprint --help`
Displays available commands and flags.

### `chatprint --version`
Prints the application version.

### `chatprint convert <INPUT> [OPTIONS]`
Converts a saved webpage to PDF.

**Options:**
- `-o, --output <DIR|FILE>`: Specify target directory or destination `.pdf` file path.
- `--output-file <FILE>`: Explicitly specify destination PDF path.
- `-s, --source [auto|gemini|chatgpt]`: Override automatic source detection (default: `auto`).
- `-f, --force`: Overwrite existing output PDF without appending numerical suffix.
- `-d, --debug`: Display detailed extraction statistics and diagnostics.

**Examples:**
```bash
# Basic conversion (creates conversation.pdf next to input)
chatprint convert chat.mhtml

# Specify direct destination PDF file
chatprint convert chat.mhtml -o "D:\MyDocs\Quantum_Report.pdf" --force

# Specify custom output folder
chatprint convert chat.mhtml --output "D:\PDFs"

# Force Gemini provider mode
chatprint convert chat.html --source gemini
```

### `chatprint inspect <INPUT>`
Inspects and analyzes a saved conversation file without generating a PDF.

**Example:**
```bash
chatprint inspect "C:\Users\User\Downloads\chat.mhtml"
```
**Output:**
```text
ChatPrint Inspection
────────────────────────────────────────
Input file:          C:\Users\User\Downloads\chat.mhtml
Format:              MHTML
Title:               is kilowatt a good company
Detected provider:   Google Gemini AI Mode
Confidence:          100%
Total messages:      14
User messages:       7
Assistant messages:  7
Embedded resources:  174
```

### `chatprint doctor`
Runs a diagnostic self-check on the host environment:
```bash
chatprint doctor
```
**Output:**
```text
ChatPrint CLI Doctor

✓ Python: 3.10.8 (exact target 3.10.8)
✓ Platform: Windows x64 (AMD64)
✓ Installation: OK (C:\Users\User\AppData\Local\ChatPrintCLI)
✓ PDF engine: ReportLab 4.4.10 OK
✓ Dependencies: All core packages verified
✓ CLI PATH: Executable on PATH

System ready.
```

---

## Uninstallation

If you ever wish to remove ChatPrint CLI from your system:

### Option A: Using the Uninstaller (Recommended on Windows)
Simply run **`uninstall.bat`** from the `ChatPrint-CLI-main` folder, or in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall-windows.ps1
```
This automatically:
1. Removes ChatPrint CLI from your User `PATH` environment variable.
2. Prompts for confirmation and deletes the isolated virtual environment folder.

### Option B: Manual Removal (Command Prompt / PowerShell)
1. **Remove from PATH**:
   ```powershell
   $UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
   $NewPath = ($UserPath -split ';' | Where-Object { $_ -and $_ -notlike "*ChatPrintCLI*" }) -join ';'
   [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
   ```
2. **Delete Installation Folder**:
   - Default directory: `C:\Users\<YourUsername>\AppData\Local\ChatPrintCLI`
   - Or whatever custom directory was chosen during installation (e.g. `E:\ChatPrintCLI`).

---

## Architecture

```
                    ChatPrint CLI
                             │
                             ▼
                      CLI Interface (Click + Rich)
                             │
                             ▼
                    Format Detector (.mhtml, .html)
                             │
               ┌─────────────┴─────────────┐
               ▼                           ▼
          MHTML Reader                HTML Reader
        (email.message MIME)        (Encoding-aware)
               │                           │
               └─────────────┬─────────────┘
                             ▼
                     Provider Detection
                             │
               ┌─────────────┴─────────────┐
               ▼                           ▼
         GeminiProvider              ChatGPTProvider
       (Search & Chat Mode)         (Turns & Markdown)
               │                           │
               └─────────────┬─────────────┘
                             ▼
                   DOM Cleaner & Extractor
              (Strips ads, sidebars, chrome)
                             │
                             ▼
                 Normalized Conversation Model
                   (Roles, ContentBlocks)
                             │
                             ▼
                    Extraction Validator
                             │
                             ▼
                    PDF Renderer Engine
                    (ReportLab Platypus)
                             │
                             ▼
                 High-Quality Vector PDF
```

---

## Security & Privacy Guarantees

- **No Network Requests**: The conversion process does not make network calls.
- **Untrusted Input Containment**:
  - Scripts (`<script>`) are automatically discarded and never executed.
  - Hidden tracking pixels, iframes, and active browser components are purged.
  - Resource extraction strictly prevents directory traversal attacks (`../`).
- **Cryptographic Verification**: The runtime bootstrapper validates SHA-256 checksums from official python.org distribution mirrors.
- **Zero Telemetry**: No analytics or metrics are collected.

---

## Development & Testing

### Running Tests
```bash
# Run full test suite
python -m pytest

# Run with verbose output
python -m pytest -v
```

### Code Formatting & Linting
```bash
python -m ruff check src tests
```

### Building the Distribution Packages (Maintainers Only)
> [!NOTE]
> End-users do **not** need to run this command. This command is strictly for project maintainers when preparing a new GitHub release or distributing wheels.

```bash
python -m build
```
This compiles the project into distribution assets inside the `dist/` folder:
- `chatprint-0.1.0-py3-none-any.whl` (pre-compiled wheel)
- `chatprint-0.1.0.tar.gz` (source archive)
These files can then be uploaded directly to GitHub Releases.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
