# Troubleshooting Guide

Common issues, diagnostics, and recovery solutions for **AI Conversation CLI**.

---

## 1. Run Diagnostics First

Whenever you encounter unexpected behavior or environment issues, run:
```bash
ai-conversation doctor -v
```
This verifies your Python version, architecture, required dependencies, PDF engine, and PATH availability.

---

## 2. Common Issues & Solutions

### Issue: "Unsupported file format"
**Cause**: The input file extension or content is not `.mhtml`, `.mht`, `.html`, or `.htm`.
**Solution**:
1. Confirm the file was saved using your browser's "Save Page As" feature.
2. Select "Webpage, Single File (*.mhtml)" or "Webpage, Complete (*.html)".

---

### Issue: "The MHTML file is empty" or "No HTML document found"
**Cause**: The file was saved before the webpage finished loading, or the save operation was interrupted.
**Solution**:
1. Open the file in Chrome, Edge, or Brave to check if it opens properly.
2. If empty, re-save the page in the browser after ensuring all AI responses have finished streaming.

---

### Issue: "Source could not be confidently detected"
**Cause**: The webpage structure is novel, or the document title does not contain standard AI keywords.
**Solution**:
Force the provider explicitly using the `--source` option:
```bash
# For Gemini / Google AI Mode
ai-conversation convert "page.mhtml" --source gemini

# For ChatGPT
ai-conversation convert "page.mhtml" --source chatgpt
```

---

### Issue: Want to see what was extracted without creating a PDF
Use the `inspect` command:
```bash
ai-conversation inspect "page.mhtml"
```
Or run with `--debug`:
```bash
ai-conversation convert "page.mhtml" --debug
```

---

### Issue: Output PDF already exists and is not overwritten
**Default Behavior**: AI Conversation CLI avoids destroying existing files by creating `filename-1.pdf`, `filename-2.pdf`, etc.
**Solution**:
Pass `--force` to explicitly allow overwriting:
```bash
ai-conversation convert "page.mhtml" --force
```

---

### Issue: Command `ai-conversation` is not recognized after install
**Cause**: The installation directory is not in your current terminal's `PATH`.
**Solution**:
1. Restart your terminal window to reload PATH.
2. Run `ai-conversation doctor` or check `%LOCALAPPDATA%\AIConversationCLI\venv\Scripts` (Windows) or `~/.local/share/ai-conversation-cli/venv/bin` (Linux/macOS).
3. Alternatively, invoke directly with Python:
   ```bash
   python -m ai_conversation convert "chat.mhtml"
   ```
