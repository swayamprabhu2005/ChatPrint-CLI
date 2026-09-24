# Extraction Engine & Heuristics

This document details the multi-stage extraction pipeline used by ChatPrint CLI to extract conversations and eliminate surrounding webpage chrome.

---

## The Core Extraction Challenge

When a user saves a Google Gemini or ChatGPT webpage locally via Chrome, Edge, or Firefox (`Ctrl + S`), the resulting file includes:
- Top headers, search bars, and logo banners.
- Account avatar menus with email addresses and sign-in status.
- Sidebars with chat histories, recommended search results, and knowledge panels.
- Action buttons: "Copy to clipboard", "Regenerate response", thumbs up/down, edit icons.
- Footers and disclaimer texts ("ChatGPT can make mistakes", "Google Search terms").

Rather than screenshotting or relying on a single fragile class name, ChatPrint CLI employs an 8-stage extraction pipeline:

```
Stage 1: Document Decoding & Resource Extraction
Stage 2: Tag & Active Element Stripping
Stage 3: Source & Provider Detection
Stage 4: Provider-Specific Element Cleaning
Stage 5: Turn Container Candidate Scoring
Stage 6: DOM-to-Block Normalization
Stage 7: Quality & Plausibility Validation
Stage 8: Platypus PDF Assembly
```

---

## Normalization: ContentBlock Model

Extracted turns are translated into a sequence of structured `ContentBlock` objects:

| Block Type | Extracted Source Elements | Description |
| :--- | :--- | :--- |
| `ParagraphBlock` | `<p>`, regular text divs, blockquotes | Standard running text with preserved bold, italic, code formatting |
| `HeadingBlock` | `<h1>`, `<h2>`, `<h3>`, `<h4>`, `<h5>`, `<h6>` | Section titles with normalized levels |
| `ListBlock` | `<ul>`, `<ol>`, `<li>` | Bulleted and numbered lists with indentation |
| `CodeBlock` | `<pre>`, `<code>` | Preformatted code blocks with detected language badge |
| `TableBlock` | `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<td>`, `<th>` | Tabular data with aligned headers and cells |
| `CitationBlock` | `<a>`, reference chips | Footnotes and reference citations |
| `ImageBlock` | `<img>` (from MHTML MIME attachments) | Embedded diagram or screenshot image |

---

## Validation Rules

Before sending data to the PDF generator, the extraction must pass validation:
1. **Minimum Turn Count**: At least one message turn must exist.
2. **Minimum Content Density**: Extracted text must exceed 10 meaningful characters.
3. **Navigation Elimination**: Text must not consist predominantly of navigation strings (`"sign in"`, `"privacy"`, `"settings"`).
4. **Confidence Thresholding**: If source confidence is below 60%, a warning is shown in the terminal.
