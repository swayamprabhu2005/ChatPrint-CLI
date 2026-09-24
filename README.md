# AI Conversation CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)]()

Convert locally saved AI conversation webpages (**Google Gemini AI Mode** and **ChatGPT**) into clean, readable, professional, searchable PDFs.

---

## Overview

Modern web browsers allow saving webpages locally (e.g., using `Ctrl + S` and selecting **"Single File"** or **"Webpage, Complete"**), creating `.mhtml`, `.mht`, or `.html` files.

However, saved conversation pages from Google Gemini and ChatGPT are cluttered with search bars, user account chips, recommendation sidebars, feedback buttons, and browser chrome.

**AI Conversation CLI** parses these locally saved files offline, extracts the complete conversation turns from beginning to end, removes all irrelevant website UI, and generates a polished, vector-text PDF suitable for archiving, printing, and sharing.

```
Saved Webpage (.mhtml / .html)
             │
             ▼
   ai-conversation convert
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

## Installation

### Option 1: Install via pipx (Recommended for CLI Tools)
```bash
pipx install git+https://github.com/swayamprabhu2005/AI-Conversation-CLI.git
```

### Option 2: Automated Bootstrap Installer
The project includes self-contained installation scripts that verify your Python runtime (target: **Python 3.10.8**), provision an isolated environment, and register the CLI on your PATH:

- **Windows (PowerShell)**:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\scripts\install-windows.ps1
  ```
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

### Option 3: Developer Installation from Source
```bash
git clone https://github.com/swayamprabhu2005/AI-Conversation-CLI.git
cd AI-Conversation-CLI

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"
```

---

## Quick Start

### 1. Save an AI Conversation Webpage
1. Open Google Gemini or ChatGPT in your browser (Chrome, Edge, Brave, Firefox).
2. Save the webpage locally:
   - In Chrome/Edge: Press `Ctrl + S` (or `Cmd + S` on macOS).
   - In the **"Save as type"** dropdown, select **"Webpage, Single File (*.mhtml)"** or **"Webpage, Complete (*.htm, *.html)"**.
3. Save the file (e.g. `conversation.mhtml`).

### 2. Convert to PDF
```bash
ai-conversation convert "C:\Users\User\Downloads\conversation.mhtml"
```

**Terminal Output:**
```text
AI Conversation CLI
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

### `ai-conversation --help`
Displays available commands and flags.

### `ai-conversation --version`
Prints the application version.

### `ai-conversation convert <INPUT> [OPTIONS]`
Converts a saved webpage to PDF.

**Options:**
- `-o, --output <DIR>`: Specify target directory for the generated PDF.
- `--output-file <FILE>`: Explicitly specify destination PDF path.
- `-s, --source [auto|gemini|chatgpt]`: Override automatic source detection (default: `auto`).
- `-f, --force`: Overwrite existing output PDF without appending numerical suffix.
- `-d, --debug`: Display detailed extraction statistics and diagnostics.

**Examples:**
```bash
# Basic conversion (creates conversation.pdf next to input)
ai-conversation convert chat.mhtml

# Specify custom output folder
ai-conversation convert chat.mhtml --output "D:\PDFs"

# Specify explicit file name and force overwrite
ai-conversation convert chat.mhtml --output-file "D:\PDFs\summary.pdf" --force

# Force Gemini provider mode
ai-conversation convert chat.html --source gemini
```

### `ai-conversation inspect <INPUT>`
Inspects and analyzes a saved conversation file without generating a PDF.

**Example:**
```bash
ai-conversation inspect "C:\Users\User\Downloads\chat.mhtml"
```
**Output:**
```text
AI Conversation Inspection
────────────────────────────────────────
Input file:          C:\Users\User\Downloads\chat.mhtml
Format:              MHTML
Title:               is kilowatt a good company - Google Search
Detected provider:   Google Gemini AI Mode
Confidence:          95%
Total messages:      2
User messages:       1
Assistant messages:  1
Embedded resources:  14
```

### `ai-conversation doctor`
Runs a diagnostic self-check on the host environment:
```bash
ai-conversation doctor
```
**Output:**
```text
AI Conversation CLI Doctor

✓ Python: 3.10.8 (exact target 3.10.8)
✓ Platform: Windows x64 (AMD64)
✓ Installation: OK (C:\Users\User\AppData\Local\AIConversationCLI)
✓ PDF engine: ReportLab 4.4.10 OK
✓ Dependencies: All core packages verified
✓ CLI PATH: Executable on PATH

System ready.
```

---

## Architecture

```
                    AI Conversation CLI
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

### Building the Package
```bash
python -m build
```
This generates standard `.whl` and `.tar.gz` distribution packages in the `dist/` directory.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
