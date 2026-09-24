# Architecture Guide

This document describes the internal design, component responsibilities, and data flow of **ChatPrint CLI**.

---

## 1. High-Level Design Principles

- **Zero Remote Dependencies**: The application executes locally without calling external APIs or browser automation.
- **Provider-Based Extraction**: AI platforms frequently change their DOM structure; separating platform-specific extraction rules into isolated providers ensures easy maintenance and updates.
- **Normalized Intermediate Model**: Downstream rendering (PDF generation) does not interact with raw HTML or DOM nodes. Instead, it consumes an immutable, provider-agnostic `Conversation` model consisting of structured `ContentBlock` elements.
- **Engine Reliability**: ReportLab Platypus is chosen for PDF generation because it runs cleanly across Windows, macOS, and Linux without native GTK+/Cairo shared library requirements.

---

## 2. Pipeline Flow

```
Input File (.mhtml / .html)
             │
             ▼
     [detector.py] ────────► Detects MIME MHTML vs HTML
             │
             ▼
     [mhtml_reader.py] / [html_reader.py]
             │
             ├── Primary HTML Document
             └── Embedded Resources (images, CSS)
             │
             ▼
    [providers/__init__.py] ─► Evaluates confidence across providers
             │
             ├── GeminiProvider (Google Search AI Mode / Gemini)
             ├── ChatGPTProvider (OpenAI ChatGPT)
             └── GenericProvider (Fallback)
             │
             ▼
    [cleaner.py] ──────────► Purges <script>, <style>, <iframe>, ads, search chrome
             │
             ▼
    [normalizer.py] ───────► Converts DOM tags into ParagraphBlock, HeadingBlock,
                             CodeBlock, ListBlock, TableBlock
             │
             ▼
    [validator.py] ────────► Asserts message count >= 1 and content integrity
             │
             ▼
    [models.py] ───────────► Builds Conversation(messages=[...])
             │
             ▼
    [renderer.py] ─────────► Builds ReportLab Platypus document with NumberedCanvas
             │
             ▼
        Output PDF
```

---

## 3. Core Components

### 3.1 Input Detection & Parsing (`src/chatprint/input/`)
- `detector.py`: Inspects file extension and first 4KB of content for multipart MIME markers (`Snapshot-Content-Location`, `MIME-Version: 1.0`, `multipart/related`).
- `mhtml_reader.py`: Leverages standard Python `email.message` to recursively traverse parts, decode base64/quoted-printable payloads, extract the primary HTML tree, and cache binary attachments.
- `html_reader.py`: Handles standalone HTML files with automated charset detection (UTF-8, ISO-8859-1, Windows-1252).

### 3.2 Provider Engine (`src/chatprint/providers/`)
All providers inherit from `ConversationProvider`:
```python
class ConversationProvider(ABC):
    @abstractmethod
    def detect_confidence(self, soup, raw_html, metadata) -> float: ...

    @abstractmethod
    def extract(self, soup, resources, original_filename) -> Conversation: ...
```
- **GeminiProvider**: Filters Google search headers, tabs, profile icons, and sidebars (`#rhs`). Extracts the user search query and AI Overview / Gemini response turns.
- **ChatGPTProvider**: Identifies turns via `data-message-author-role` and `data-testid` conversation containers. Extracts code blocks and markdown tables.
- **GenericProvider**: Uses text density and container scoring heuristics (`score_conversation_container`) to detect chat dialogues on unrecognized pages.

### 3.3 Extraction, Cleaning & Validation (`src/chatprint/extraction/`)
- `cleaner.py`: Removes non-content tags, hidden tags (`display: none`), and provider-specific unwanted CSS selectors.
- `normalizer.py`: Transforms HTML elements into structured `ContentBlock` subclasses.
- `validator.py`: Ensures extracted conversation has non-empty text, plausible turn count, and absence of pure navigation UI.

### 3.4 PDF Generation Engine (`src/chatprint/pdf/`)
- `renderer.py`: Uses ReportLab `SimpleDocTemplate` and Platypus flowables (`Paragraph`, `Table`, `Preformatted`, `HRFlowable`).
- `styles.py`: Defines color palettes and typographies. Uses a custom two-pass `NumberedCanvas` to calculate total pages dynamically and print "Page X of Y" with a professional header/footer.
