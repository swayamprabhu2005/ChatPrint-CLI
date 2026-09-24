# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-24

### Added
- Initial release of ChatPrint CLI (`chatprint`).
- Robust MHTML (`.mhtml`, `.mht`) MIME parser and standard HTML (`.html`, `.htm`) reader.
- Multi-provider conversation extraction architecture with confidence scoring:
  - `GeminiProvider`: Google Gemini AI Mode / AI Overview parser with extraction of multi-turn dialogues, code, tables, and elimination of search chrome, accounts, and recommendations.
  - `ChatGPTProvider`: ChatGPT parser with conversation turn identification, prose formatting, code blocks, and elimination of sidebars, model selectors, and action buttons.
  - `GenericProvider`: Heuristic-based conversational turn extractor for other AI chat pages.
- Normalized internal conversation representation (`Conversation`, `Message`, `ContentBlock`).
- PDF generation engine built on ReportLab Platypus:
  - Clean typographic hierarchy and card styling for User and Assistant messages.
  - Formatted code snippets, lists, tables, and headers.
  - Dynamic page numbering header/footer ("Page X of Y").
  - 100% offline, searchable, vector-text PDF output.
- CLI commands:
  - `chatprint convert <FILE>` with options `--output`, `--output-file`, `--source`, `--force`, `--debug`.
  - `chatprint inspect <FILE>` for diagnostic inspection without PDF generation.
  - `chatprint doctor` for system health check.
  - `--version` and `--help`.
- Cross-platform setup and installation bootstrapper with Python 3.10.8 runtime detection, cryptographic SHA-256 validation, and PATH registration (`install-windows.ps1`, `install-macos.sh`, `install-linux.sh`).
- Comprehensive unit and integration test suite with golden fixtures.
